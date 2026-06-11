from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.data.chest_catalog import (
    BOSS_CHEST_CATALOG,
    NORMAL_CHEST_CATALOG,
    boss_farm_levels,
    catalog_keys,
    load_boss_chest_catalog,
)
from src.data.stage_catalog import (
    find_catalog_entry,
    suggested_stage_for_chest_level,
)
from src.domain.chest_farm import ChestFarmSlot, enabled_farm_maps
from src.domain.drop_filter import StrategySettings
from src.domain.rotation_engine import MapConfig
from src.ui.i18n import Language
from src.ui.theme import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH


@dataclass(frozen=True)
class MonitorSettings:
    poll_interval_seconds: float
    debounce_seconds: float
    average_drop_minutes: float
    window_title: str
    dry_run: bool
    save_poll_interval_seconds: float


@dataclass(frozen=True)
class AppConfig:
    player_log_path: Path
    save_file_path: Path
    game_exe_path: Path
    state_file_path: Path
    es3_password: str
    language: Language
    window_width: int
    window_height: int
    monitor: MonitorSettings
    strategy: StrategySettings
    chest_item_keys: dict[str, list[str]]
    global_ui: dict[str, dict[str, int | float]]
    chest_farms: list[ChestFarmSlot]
    maps: list[MapConfig]


def _parse_chest_farm_entry(entry: dict[str, Any]) -> ChestFarmSlot:
    return ChestFarmSlot(
        chest_level=int(entry["chest_level"]),
        stage_key=int(entry["stage_key"]),
        enabled=bool(entry.get("enabled", False)),
        priority=int(entry.get("priority", 99)),
    )


def _chest_farm_to_dict(slot: ChestFarmSlot) -> dict[str, Any]:
    return {
        "chest_level": slot.chest_level,
        "stage_key": slot.stage_key,
        "enabled": slot.enabled,
        "priority": slot.priority,
    }


def _default_chest_farms() -> list[ChestFarmSlot]:
    slots: list[ChestFarmSlot] = []
    for index, level in enumerate((40, 50), start=1):
        suggested = suggested_stage_for_chest_level(level)
        slots.append(
            ChestFarmSlot(
                chest_level=level,
                stage_key=suggested.stage_key if suggested else 0,
                enabled=True,
                priority=index,
            )
        )
    return slots


def _load_chest_farms(raw: dict[str, Any]) -> list[ChestFarmSlot]:
    loaded: list[ChestFarmSlot] = []

    for entry in raw.get("chest_farms", []):
        slot = _parse_chest_farm_entry(entry)
        if not entry.get("enabled", True):
            continue
        if slot.chest_level not in boss_farm_levels():
            continue
        catalog_entry = find_catalog_entry(slot.stage_key)
        if (
            catalog_entry is None
            or catalog_entry.is_act_boss
            or catalog_entry.boss_chest_level != slot.chest_level
        ):
            suggested = suggested_stage_for_chest_level(slot.chest_level)
            slot = ChestFarmSlot(
                chest_level=slot.chest_level,
                stage_key=suggested.stage_key if suggested else 0,
                enabled=True,
                priority=slot.priority,
            )
        loaded.append(
            ChestFarmSlot(
                chest_level=slot.chest_level,
                stage_key=slot.stage_key,
                enabled=True,
                priority=slot.priority,
            )
        )

    if not loaded:
        for entry in raw.get("maps", []):
            stage_key = int(entry.get("stage_key", 0))
            catalog_entry = find_catalog_entry(stage_key)
            if catalog_entry is None:
                continue
            level = catalog_entry.boss_chest_level
            if level not in boss_farm_levels():
                continue
            loaded.append(
                ChestFarmSlot(
                    chest_level=level,
                    stage_key=stage_key,
                    enabled=True,
                    priority=int(entry.get("priority", len(loaded) + 1)),
                )
            )

    if not loaded:
        return _default_chest_farms()

    seen_levels: set[int] = set()
    unique: list[ChestFarmSlot] = []
    for slot in sorted(loaded, key=lambda item: item.priority):
        if slot.chest_level in seen_levels:
            continue
        seen_levels.add(slot.chest_level)
        unique.append(
            ChestFarmSlot(
                chest_level=slot.chest_level,
                stage_key=slot.stage_key,
                enabled=True,
                priority=len(unique) + 1,
            )
        )
    return unique


def default_chest_item_keys() -> dict[str, list[str]]:
    obtainable = [item.key for item in load_boss_chest_catalog() if item.obtainable]
    act_boss = [item.key for item in load_boss_chest_catalog() if item.key.startswith("93")]
    boss_keys = sorted(set(obtainable) | set(act_boss))
    return {
        "boss": boss_keys,
        "normal_brown": catalog_keys(NORMAL_CHEST_CATALOG),
    }


def load_raw_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_config(config_path: Path) -> AppConfig:
    from src.infrastructure.game_paths import (
        discover_es3_password,
        discover_game_exe,
        discover_player_log,
        discover_save_file,
        resolve_path,
    )
    from src.runtime_paths import resolve_app_relative_path

    raw = load_raw_config(config_path)
    paths = raw.get("paths", {})
    monitor_raw = raw.get("monitor", {})
    strategy_raw = raw.get("strategy", {})
    ui_raw = raw.get("ui", {})
    chest_farms = _load_chest_farms(raw)
    raw_chest_keys = raw.get("chest_item_keys", default_chest_item_keys())
    obtainable_boss_keys = default_chest_item_keys()["boss"]
    boss_keys = obtainable_boss_keys

    return AppConfig(
        player_log_path=resolve_path(paths.get("player_log"), discover=discover_player_log),
        save_file_path=resolve_path(paths.get("save_file"), discover=discover_save_file),
        game_exe_path=resolve_path(paths.get("game_exe"), discover=discover_game_exe),
        state_file_path=resolve_app_relative_path(paths.get("state_file", "state.json")),
        es3_password=str(paths.get("es3_password", discover_es3_password())),
        language=Language.from_code(ui_raw.get("language")),
        window_width=int(ui_raw.get("window_width", DEFAULT_WINDOW_WIDTH)),
        window_height=int(ui_raw.get("window_height", DEFAULT_WINDOW_HEIGHT)),
        monitor=MonitorSettings(
            poll_interval_seconds=float(monitor_raw.get("poll_interval_seconds", 0.5)),
            debounce_seconds=float(monitor_raw.get("debounce_seconds", 4.0)),
            average_drop_minutes=float(monitor_raw.get("average_drop_minutes", 12)),
            window_title=str(monitor_raw.get("window_title", "TaskBarHero")),
            dry_run=bool(monitor_raw.get("dry_run", False)),
            save_poll_interval_seconds=float(monitor_raw.get("save_poll_interval_seconds", 2.0)),
        ),
        strategy=StrategySettings(
            consider_common_chest=bool(strategy_raw.get("consider_common_chest", False)),
        ),
        chest_item_keys={
            "boss": boss_keys,
            "normal_brown": raw_chest_keys.get(
                "normal_brown",
                default_chest_item_keys()["normal_brown"],
            ),
        },
        global_ui=raw.get("global_ui", {}),
        chest_farms=chest_farms,
        maps=enabled_farm_maps(chest_farms),
    )


def save_config(config_path: Path, app_config: AppConfig) -> None:
    raw = load_raw_config(config_path) if config_path.exists() else {}
    raw["paths"] = {
        "player_log": str(app_config.player_log_path).replace("\\", "/"),
        "save_file": str(app_config.save_file_path).replace("\\", "/"),
        "game_exe": str(app_config.game_exe_path).replace("\\", "/"),
        "state_file": str(app_config.state_file_path).replace("\\", "/"),
        "es3_password": app_config.es3_password,
    }
    raw["monitor"] = {
        "poll_interval_seconds": app_config.monitor.poll_interval_seconds,
        "debounce_seconds": app_config.monitor.debounce_seconds,
        "average_drop_minutes": app_config.monitor.average_drop_minutes,
        "window_title": app_config.monitor.window_title,
        "dry_run": app_config.monitor.dry_run,
        "save_poll_interval_seconds": app_config.monitor.save_poll_interval_seconds,
    }
    raw["strategy"] = {
        "consider_common_chest": app_config.strategy.consider_common_chest,
    }
    raw["ui"] = {
        "language": app_config.language.value,
        "window_width": app_config.window_width,
        "window_height": app_config.window_height,
    }
    raw["chest_item_keys"] = app_config.chest_item_keys
    raw["global_ui"] = app_config.global_ui
    raw["chest_farms"] = [
        _chest_farm_to_dict(slot)
        for slot in sorted(app_config.chest_farms, key=lambda item: item.priority)
    ]
    raw.pop("maps", None)

    with config_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(raw, handle, sort_keys=False, allow_unicode=True)
