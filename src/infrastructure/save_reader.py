from __future__ import annotations

import json
import logging
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from es3_modifier.main import ES3

from src.domain.chest_event import ChestEvent, ChestType
from src.infrastructure.game_paths import (
    SAVE_FILE_NAME,
    discover_es3_password,
    list_active_save_candidates,
)

logger = logging.getLogger(__name__)


BOSS_BOX_TYPE = 1
NORMAL_BOX_TYPE = 0
SAVE_CONFIRMATION_WINDOW_SECONDS = 12.0


@dataclass(frozen=True)
class BoxDataSnapshot:
    box_types: tuple[int, ...]
    box_quantities: tuple[int, ...]

    @classmethod
    def from_raw(cls, raw: dict) -> BoxDataSnapshot:
        return cls(
            box_types=tuple(int(value) for value in raw.get("BoxTypes", [])),
            box_quantities=tuple(int(value) for value in raw.get("BoxQuantity", [])),
        )

    def boss_box_count(self) -> int:
        return sum(
            quantity
            for box_type, quantity in zip(self.box_types, self.box_quantities, strict=False)
            if box_type == BOSS_BOX_TYPE
        )

    def normal_box_count(self) -> int:
        return sum(
            quantity
            for box_type, quantity in zip(self.box_types, self.box_quantities, strict=False)
            if box_type == NORMAL_BOX_TYPE
        )


@dataclass(frozen=True)
class SaveSnapshot:
    current_stage_key: int
    box_data: BoxDataSnapshot

    @property
    def boss_box_count(self) -> int:
        return self.box_data.boss_box_count()


@dataclass(frozen=True)
class SaveChestDetection:
    event: ChestEvent
    stage_key: int


def _save_source_priority(path: Path) -> int:
    if path.name == SAVE_FILE_NAME:
        return 2
    return 1


def pick_preferred_snapshot(
    snapshots: list[tuple[Path, SaveSnapshot]],
) -> tuple[Path, SaveSnapshot]:
    if not snapshots:
        raise FileNotFoundError("No readable save snapshots found")

    def ranking(item: tuple[Path, SaveSnapshot]) -> tuple[float, int]:
        path, _snapshot = item
        return (path.stat().st_mtime, _save_source_priority(path))

    return max(snapshots, key=ranking)


class SaveReader:
    def __init__(self, save_path: Path, password: str | None = None) -> None:
        self._save_path = save_path
        self._password = password or discover_es3_password()
        self._last_source_path: Path | None = None

    @property
    def last_source_path(self) -> Path | None:
        return self._last_source_path

    def _read_encrypted_bytes(self, save_path: Path) -> bytes:
        try:
            return save_path.read_bytes()
        except PermissionError:
            return self._read_via_temp_copy(save_path)

    def _read_via_temp_copy(self, save_path: Path) -> bytes:
        temp_dir = Path(tempfile.gettempdir())
        temp_copy = temp_dir / f"tbh_monitor_{save_path.name}"
        shutil.copy2(save_path, temp_copy)
        try:
            return temp_copy.read_bytes()
        finally:
            temp_copy.unlink(missing_ok=True)

    def _read_snapshot_from(self, save_path: Path) -> SaveSnapshot:
        encrypted = self._read_encrypted_bytes(save_path)
        player_payload = ES3(encrypted, self._password).load()["PlayerSaveData"]["value"]
        player = json.loads(player_payload)
        common = player["commonSaveData"]

        return SaveSnapshot(
            current_stage_key=int(common["currentStageKey"]),
            box_data=BoxDataSnapshot.from_raw(player.get("BoxData", {})),
        )

    def read_snapshot(self) -> SaveSnapshot:
        candidates = list_active_save_candidates(self._save_path)
        if not candidates:
            raise FileNotFoundError(self._save_path)

        readable: list[tuple[Path, SaveSnapshot]] = []
        last_error: Exception | None = None
        for candidate in candidates:
            try:
                readable.append((candidate, self._read_snapshot_from(candidate)))
            except Exception as error:
                last_error = error
                logger.debug("Failed to read save candidate %s: %s", candidate.name, error)

        if not readable:
            if last_error is not None:
                raise last_error
            raise FileNotFoundError(self._save_path)

        source_path, snapshot = pick_preferred_snapshot(readable)
        if self._last_source_path != source_path:
            logger.debug(
                "Using save snapshot from %s (boss=%s, normal=%s)",
                source_path.name,
                snapshot.boss_box_count,
                snapshot.box_data.normal_box_count(),
            )
        self._last_source_path = source_path
        return snapshot


class SaveChestDetector:
    def __init__(
        self,
        consider_common_chest: bool,
        debounce_seconds: float = 4.0,
    ) -> None:
        self._consider_common_chest = consider_common_chest
        self._debounce_seconds = debounce_seconds
        self._previous: SaveSnapshot | None = None
        self._last_event_at_by_key: dict[str, float] = {}
        self._last_boss_box_increase_at: float | None = None
        self._last_normal_box_increase_at: float | None = None

    def _is_debounced(self, debounce_key: str) -> bool:
        last_event_at = self._last_event_at_by_key.get(debounce_key)
        if last_event_at is None:
            return False
        return time.time() - last_event_at < self._debounce_seconds

    def _mark_detected(self, debounce_key: str) -> None:
        self._last_event_at_by_key[debounce_key] = time.time()

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._consider_common_chest = enabled

    def had_recent_box_increase_for(
        self,
        event: ChestEvent,
        *,
        within_seconds: float = SAVE_CONFIRMATION_WINDOW_SECONDS,
    ) -> bool:
        now = time.time()
        if event.chest_type == ChestType.BOSS:
            last_increase_at = self._last_boss_box_increase_at
        elif event.chest_type == ChestType.NORMAL_BROWN:
            last_increase_at = self._last_normal_box_increase_at
        else:
            return False
        return last_increase_at is not None and now - last_increase_at <= within_seconds

    def inspect(self, snapshot: SaveSnapshot) -> SaveChestDetection | None:
        detections = self.inspect_all(snapshot)
        return detections[0] if detections else None

    def inspect_all(self, snapshot: SaveSnapshot) -> list[SaveChestDetection]:
        if self._previous is None:
            self._previous = snapshot
            return []

        previous = self._previous
        events = self._find_all_events(previous, snapshot)
        stage_key = self._resolve_stage_key_for_box_events(previous, snapshot, events)
        self._previous = snapshot

        accepted: list[SaveChestDetection] = []
        for event in events:
            if event.chest_type == ChestType.BOSS:
                debounce_key = f"boss:{stage_key}:{event.count}"
            elif event.chest_type == ChestType.NORMAL_BROWN:
                debounce_key = f"normal:{stage_key}:{event.count}"
            else:
                debounce_key = f"{event.chest_type.value}:{stage_key}:{event.count}"
            if self._is_debounced(debounce_key):
                continue
            self._mark_detected(debounce_key)
            accepted.append(SaveChestDetection(event=event, stage_key=stage_key))
        return accepted

    def _resolve_stage_key_for_box_events(
        self,
        previous: SaveSnapshot,
        snapshot: SaveSnapshot,
        events: list[ChestEvent],
    ) -> int:
        if not events:
            return snapshot.current_stage_key

        box_increased = (
            snapshot.boss_box_count > previous.boss_box_count
            or snapshot.box_data.normal_box_count() > previous.box_data.normal_box_count()
        )
        if box_increased and snapshot.current_stage_key != previous.current_stage_key:
            return previous.current_stage_key
        return snapshot.current_stage_key

    def _find_all_events(
        self,
        previous: SaveSnapshot,
        snapshot: SaveSnapshot,
    ) -> list[ChestEvent]:
        events: list[ChestEvent] = []
        now = time.time()

        if snapshot.boss_box_count > previous.boss_box_count:
            self._last_boss_box_increase_at = now
            events.append(
                ChestEvent(
                    item_key="boss_box_data",
                    chest_type=ChestType.BOSS,
                    count=snapshot.boss_box_count,
                    raw_line=(
                        f"Baú de chefe no save: "
                        f"{previous.boss_box_count} → {snapshot.boss_box_count}"
                    ),
                )
            )

        if (
            self._consider_common_chest
            and snapshot.box_data.normal_box_count() > previous.box_data.normal_box_count()
        ):
            self._last_normal_box_increase_at = now
            events.append(
                ChestEvent(
                    item_key="normal_box_data",
                    chest_type=ChestType.NORMAL_BROWN,
                    count=snapshot.box_data.normal_box_count(),
                    raw_line=(
                        f"Baú comum no save: "
                        f"{previous.box_data.normal_box_count()} → "
                        f"{snapshot.box_data.normal_box_count()}"
                    ),
                )
            )

        return events
