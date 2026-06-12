from __future__ import annotations

from dataclasses import dataclass

from src.data.stage_catalog import find_catalog_entry
from src.domain.rotation_engine import MapConfig


@dataclass(frozen=True)
class ChestFarmSlot:
    chest_level: int
    stage_key: int
    enabled: bool = False
    priority: int = 99
    clear_time_seconds: int | None = None


def chest_farm_slot_to_map_config(slot: ChestFarmSlot) -> MapConfig:
    entry = find_catalog_entry(slot.stage_key)
    if entry is None:
        raise ValueError(f"Unknown stage_key {slot.stage_key} for chest Lv {slot.chest_level}")

    if entry.boss_chest_level != slot.chest_level:
        raise ValueError(
            f"Map {entry.label} drops {entry.boss_chest_name}, not level {slot.chest_level}"
        )

    boss_keys = (entry.boss_chest_key,)
    return MapConfig(
        priority=slot.priority,
        label=f"{entry.label} · {entry.boss_chest_name}",
        act=entry.act,
        stage=entry.stage,
        difficulty=entry.difficulty,
        stage_key=slot.stage_key,
        ui={},
        enabled=slot.enabled,
        boss_chest_keys=boss_keys,
        best_boss_drop_keys=boss_keys,
    )


def enabled_farm_maps(slots: list[ChestFarmSlot]) -> list[MapConfig]:
    maps: list[MapConfig] = []
    for slot in sorted(slots, key=lambda item: item.priority):
        if slot.stage_key <= 0:
            continue
        active = ChestFarmSlot(
            chest_level=slot.chest_level,
            stage_key=slot.stage_key,
            enabled=True,
            priority=slot.priority,
        )
        try:
            maps.append(chest_farm_slot_to_map_config(active))
        except ValueError:
            continue
    return maps
