from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from src.config_loader import AppConfig
from src.domain.chest_level_resolver import drop_chest_level_for_event
from src.data.stage_codec import decode_stage_key
from src.data.stage_catalog import boss_chest_drop_percent_for_stage_key, find_catalog_entry
from src.domain.chest_drop_correlator import ChestDropCorrelator, ConfirmedChestDrop
from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_event_validator import is_chest_event_consistent_with_stage
from src.domain.drop_filter import should_rotate_on_drop
from src.domain.rotation_engine import MapConfig, RotationEngine, RotationResult
from src.infrastructure.log_watcher import PlayerLogPoller
from src.infrastructure.save_reader import SaveChestDetector, SaveReader
from src.ui.i18n import (
    Language,
    chest_kind_label,
    format_chest_drop_log,
    format_map_drop_label,
    localized_map_label,
    localized_map_label_for_stage_key,
    t,
)
from src.ui.map_display import map_game_instruction

logger = logging.getLogger(__name__)


@dataclass
class PersistedState:
    current_index: int = 0
    last_drop_at: float | None = None
    last_map_label: str | None = None


class DropDeduplicator:
    def __init__(self, window_seconds: float = 6.0) -> None:
        self._window_seconds = window_seconds
        self._recent: list[tuple[float, str]] = []

    def is_duplicate(self, dedup_key: str) -> bool:
        now = time.time()
        self._recent = [
            entry
            for entry in self._recent
            if now - entry[0] < self._window_seconds
        ]
        for _, recent_key in self._recent:
            if recent_key == dedup_key:
                return True
        self._recent.append((now, dedup_key))
        return False


class StateStore:
    def __init__(self, state_file_path: Path) -> None:
        self._state_file_path = state_file_path

    def load(self) -> PersistedState:
        if not self._state_file_path.exists():
            return PersistedState()

        with self._state_file_path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        return PersistedState(
            current_index=int(raw.get("current_index", 0)),
            last_drop_at=raw.get("last_drop_at"),
            last_map_label=raw.get("last_map_label"),
        )

    def save(self, state: PersistedState) -> None:
        with self._state_file_path.open("w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, indent=2)


class MonitorService:
    def __init__(
        self,
        config: AppConfig,
        dry_run: bool | None = None,
        on_status: Callable[[str], None] | None = None,
        on_chest_drop: Callable[[ChestEvent, int], None] | None = None,
        on_drop_log: Callable[[str], None] | None = None,
        on_stage_changed: Callable[[int], None] | None = None,
    ) -> None:
        self._config = config
        self._language = config.language
        self._dry_run = config.monitor.dry_run if dry_run is None else dry_run
        self._on_status = on_status
        self._on_chest_drop = on_chest_drop
        self._on_drop_log = on_drop_log
        self._on_stage_changed = on_stage_changed
        self._state_store = StateStore(config.state_file_path)
        persisted = self._state_store.load()
        self._rotation = RotationEngine(config.maps, current_index=persisted.current_index)
        self._save_reader = SaveReader(config.save_file_path, password=config.es3_password)
        self._save_detector = SaveChestDetector(
            consider_common_chest=config.strategy.consider_common_chest,
            debounce_seconds=config.monitor.debounce_seconds,
        )
        self._log_poller = PlayerLogPoller(
            config.player_log_path,
            consider_common_chest=config.strategy.consider_common_chest,
            debounce_seconds=config.monitor.debounce_seconds,
        )
        self._drop_deduplicator = DropDeduplicator(
            window_seconds=config.monitor.debounce_seconds + 2.0,
        )
        self._drop_correlator = ChestDropCorrelator(
            confirmation_window_seconds=config.monitor.debounce_seconds + 11.0,
        )
        self._pending_event: ChestEvent | None = None
        self._pending_stage_key: int | None = None
        self._debounce_until: float | None = None
        self._running = False
        self._last_reported_stage_key: int | None = None
        self._unknown_stage_logged = False
        self._active_stage_key: int | None = None

    @property
    def current_map_label(self) -> str:
        return self._rotation.current_map.label

    @property
    def consider_common_chest(self) -> bool:
        return self._config.strategy.consider_common_chest

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._config = replace(
            self._config,
            strategy=replace(
                self._config.strategy,
                consider_common_chest=enabled,
            ),
        )
        self._save_detector.set_consider_common_chest(enabled)
        self._log_poller.set_consider_common_chest(enabled)

    def _emit_status(self, message: str) -> None:
        logger.info(message)
        if self._on_status is not None:
            self._on_status(message)

    def _emit_drop_log(self, message: str) -> None:
        logger.info(message)
        if self._on_drop_log is not None:
            self._on_drop_log(message)

    def _notify_stage_changed(self, stage_key: int) -> None:
        if self._active_stage_key == stage_key:
            return
        self._active_stage_key = stage_key
        if self._on_stage_changed is not None:
            self._on_stage_changed(stage_key)

    def _resolve_active_map(self, stage_key: int) -> MapConfig | None:
        return self._rotation.sync_to_stage_key(stage_key)

    def _chest_level_for_event(self, event: ChestEvent, stage_key: int) -> int | None:
        return drop_chest_level_for_event(event, stage_key)

    def _dedup_key_for_event(self, event: ChestEvent, stage_key: int) -> str:
        chest_level = self._chest_level_for_event(event, stage_key)
        if event.chest_type == ChestType.NORMAL_BROWN:
            if chest_level is not None:
                return f"common:{chest_level}"
            return f"common:{event.item_key}"
        if event.chest_type == ChestType.BOSS and chest_level is not None:
            return f"boss:{chest_level}"
        return f"{event.chest_type.value}:{event.item_key}"

    def _map_name_for_stage_key(self, stage_key: int) -> str:
        entry = find_catalog_entry(stage_key)
        if entry is not None:
            return entry.name
        return decode_stage_key(stage_key).label

    def _sync_stage_from_save(self, stage_key: int) -> MapConfig | None:
        active_map = self._resolve_active_map(stage_key)
        stage = decode_stage_key(stage_key)

        if active_map is not None:
            if self._last_reported_stage_key != stage_key:
                self._emit_status(
                    t(
                        "map_in_game",
                        language=self._language,
                        label=localized_map_label(active_map, language=self._language),
                        stage_key=stage_key,
                        stage_label=stage.label,
                    )
                )
                self._last_reported_stage_key = stage_key
                self._unknown_stage_logged = False
            return active_map

        if not self._unknown_stage_logged or self._last_reported_stage_key != stage_key:
            self._emit_status(
                t(
                    "stage_not_in_rotation",
                    language=self._language,
                    stage_label=stage.label,
                    stage_key=stage_key,
                )
            )
            self._unknown_stage_logged = True
            self._last_reported_stage_key = stage_key
        return None

    def _sync_current_stage_from_save(self) -> None:
        try:
            snapshot = self._save_reader.read_snapshot()
            self._notify_stage_changed(snapshot.current_stage_key)
            active_map = self._sync_stage_from_save(snapshot.current_stage_key)
            if active_map is None:
                self._emit_status(
                    t(
                        "save_status_unknown",
                        language=self._language,
                        stage_key=snapshot.current_stage_key,
                        boss_count=snapshot.boss_box_count,
                    )
                )
            else:
                self._emit_status(
                    t(
                        "save_status_known",
                        language=self._language,
                        stage_key=snapshot.current_stage_key,
                        label=localized_map_label(active_map, language=self._language),
                        boss_count=snapshot.boss_box_count,
                    )
                )
        except Exception as error:
            self._emit_status(
                t("cannot_read_save", language=self._language, error=error)
            )

    def _emit_confirmed_drop(self, event: ChestEvent, stage_key: int) -> None:
        if event.chest_type == ChestType.NORMAL_BROWN and not self.consider_common_chest:
            return

        if not is_chest_event_consistent_with_stage(event, stage_key):
            logger.debug(
                "Chest event ignored: item_key=%s does not match stage_key=%s",
                event.item_key,
                stage_key,
            )
            return

        if self._drop_deduplicator.is_duplicate(
            self._dedup_key_for_event(event, stage_key)
        ):
            return

        chest_level = self._chest_level_for_event(event, stage_key)
        stage = decode_stage_key(stage_key)
        map_name = self._map_name_for_stage_key(stage_key)

        if chest_level is not None:
            self._emit_drop_log(
                format_chest_drop_log(
                    chest_level=chest_level,
                    map_name=map_name,
                    act=stage.act,
                    stage=stage.stage,
                    difficulty=stage.difficulty.value,
                    chest_kind=chest_kind_label(event.chest_type, language=self._language),
                    language=self._language,
                )
            )

        if self._on_chest_drop is not None:
            self._on_chest_drop(event, stage_key)

        if event.chest_type == ChestType.NORMAL_BROWN:
            return

        self._pending_event = event
        self._pending_stage_key = stage_key
        self._debounce_until = time.time() + self._config.monitor.debounce_seconds

    def _process_confirmed_drops(self, confirmed: list[ConfirmedChestDrop]) -> None:
        for drop in confirmed:
            self._emit_confirmed_drop(drop.event, drop.stage_key)

    def _process_pending_event(self) -> None:
        if self._pending_event is None or self._debounce_until is None:
            return
        if time.time() < self._debounce_until:
            return

        event = self._pending_event
        stage_key = self._pending_stage_key
        self._pending_event = None
        self._pending_stage_key = None
        self._debounce_until = None

        if stage_key is None:
            return

        active_map = self._resolve_active_map(stage_key)
        stage = decode_stage_key(stage_key)
        chest_level = self._chest_level_for_event(event, stage_key) or 0
        map_label = format_map_drop_label(
            act=stage.act,
            stage=stage.stage,
            map_name=self._map_name_for_stage_key(stage_key),
            boss_drop_percent=boss_chest_drop_percent_for_stage_key(stage_key),
            language=self._language,
        )

        if active_map is None:
            self._emit_drop_log(
                t(
                    "log_chest_ignored",
                    language=self._language,
                    time=time.strftime("%H:%M:%S"),
                    level=chest_level,
                    map_name=map_label,
                    reason=t("drop_ignored_not_in_rotation", language=self._language),
                )
            )
            return

        should_rotate, reason = should_rotate_on_drop(
            event,
            active_map,
            self._config.strategy,
            language=self._language,
        )
        if not should_rotate:
            self._emit_drop_log(
                t(
                    "log_chest_ignored",
                    language=self._language,
                    time=time.strftime("%H:%M:%S"),
                    level=chest_level,
                    map_name=map_label,
                    reason=reason,
                )
            )
            return

        rotation = self._rotation.advance_on_chest_drop()
        self._record_drop_advance(rotation, event, active_map)

    def _record_drop_advance(
        self,
        rotation: RotationResult,
        _event: ChestEvent,
        previous_map: MapConfig,
    ) -> None:
        next_map = rotation.current_map
        instruction = map_game_instruction(next_map, language=self._language)
        self._emit_status(
            t(
                "drop_advance_next",
                language=self._language,
                from_label=localized_map_label(previous_map, language=self._language),
                to_label=localized_map_label(next_map, language=self._language),
                instruction=instruction,
            )
        )

        if self._dry_run:
            self._emit_status(
                t(
                    "simulation_next_map",
                    language=self._language,
                    label=localized_map_label(next_map, language=self._language),
                    instruction=instruction,
                )
            )

        self._state_store.save(
            PersistedState(
                current_index=rotation.current_index,
                last_drop_at=time.time(),
                last_map_label=localized_map_label(next_map, language=self._language),
            )
        )

    def run(self) -> None:
        enabled_labels = ", ".join(
            localized_map_label(item, language=self._language)
            for item in self._rotation.maps
        )
        mode_label = (
            t("mode_simulation", language=self._language)
            if self._dry_run
            else t("mode_active", language=self._language)
        )
        self._emit_status(
            t(
                "monitor_started",
                language=self._language,
                mode=mode_label,
                save_name=self._config.save_file_path.name,
            )
        )
        self._emit_status(
            t(
                "rotation_configured",
                language=self._language,
                labels=enabled_labels,
            )
        )
        self._sync_current_stage_from_save()

        self._running = True
        try:
            while self._running:
                stage_key: int | None = None
                confirmed_drops: list[ConfirmedChestDrop] = []

                try:
                    snapshot = self._save_reader.read_snapshot()
                    stage_key = snapshot.current_stage_key
                    self._notify_stage_changed(stage_key)
                    self._sync_stage_from_save(stage_key)
                    for detection in self._save_detector.inspect_all(snapshot):
                        confirmed_drops.extend(
                            self._drop_correlator.register_save_drop(
                                detection.event,
                                detection.stage_key,
                            )
                        )
                except FileNotFoundError as error:
                    self._emit_status(
                        t("file_not_found", language=self._language, error=error)
                    )
                except Exception as error:
                    logger.exception("Save polling failed")
                    self._emit_status(
                        t("error_read_save", language=self._language, error=error)
                    )

                try:
                    if stage_key is not None:
                        for log_event in self._log_poller.poll():
                            confirmed_drops.extend(
                                self._drop_correlator.register_log_drop(
                                    log_event,
                                    stage_key,
                                )
                            )
                except Exception as error:
                    logger.exception("Player log polling failed")
                    self._emit_status(
                        t("error_read_player_log", language=self._language, error=error)
                    )

                confirmed_drops.extend(self._drop_correlator.collect_save_fallbacks())
                self._process_confirmed_drops(confirmed_drops)
                self._process_pending_event()
                time.sleep(self._config.monitor.save_poll_interval_seconds)
        finally:
            self._running = False
            self._log_poller.close()

    def stop(self) -> None:
        self._running = False
        self._log_poller.close()
        self._emit_status(t("monitor_stopped", language=self._language))

    def read_current_stage_label(self) -> str | None:
        try:
            snapshot = self._save_reader.read_snapshot()
            active_map = self._rotation.find_map_by_stage_key(snapshot.current_stage_key)
            if active_map is not None:
                return localized_map_label(active_map, language=self._language)
            return localized_map_label_for_stage_key(
                snapshot.current_stage_key,
                language=self._language,
            )
        except Exception:
            return None
