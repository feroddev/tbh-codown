from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.data.stage_codec import Difficulty, encode_stage_key
from src.domain.rotation_engine import MapConfig

STAGES_JSON = Path(__file__).with_name("stages.json")

DIFFICULTY_SORT_ORDER = {
    "Normal": 0,
    "Nightmare": 1,
    "Hell": 2,
    "Torment": 3,
}


@dataclass(frozen=True)
class StageCatalogEntry:
    name: str
    act: int
    stage: int
    difficulty: str
    enemy_level: int
    is_act_boss: bool
    boss_chest_key: str
    boss_chest_level: int
    boss_chest_name: str
    boss_chest_drop_percent: float | None = None

    @property
    def stage_key(self) -> int:
        return encode_stage_key(self.act, self.stage, Difficulty(self.difficulty))

    @property
    def label(self) -> str:
        return f"{self.act}-{self.stage} {self.name} — Lv{self.enemy_level}"

    def to_map_config(
        self,
        *,
        priority: int,
        enabled: bool = False,
    ) -> MapConfig:
        boss_keys = (self.boss_chest_key,)
        return MapConfig(
            priority=priority,
            label=self.label,
            act=self.act,
            stage=self.stage,
            difficulty=self.difficulty,
            stage_key=self.stage_key,
            ui={},
            enabled=enabled,
            boss_chest_keys=boss_keys,
            best_boss_drop_keys=boss_keys,
        )


@lru_cache(maxsize=1)
def load_stage_catalog() -> tuple[StageCatalogEntry, ...]:
    raw = json.loads(STAGES_JSON.read_text(encoding="utf-8"))
    entries = [
        StageCatalogEntry(
            name=item["name"],
            act=int(item["act"]),
            stage=int(item["stage"]),
            difficulty=str(item["difficulty"]),
            enemy_level=int(item["enemy_level"]),
            is_act_boss=bool(item.get("is_act_boss", False)),
            boss_chest_key=str(item["boss_chest_key"]),
            boss_chest_level=int(item["boss_chest_level"]),
            boss_chest_name=str(item["boss_chest_name"]),
            boss_chest_drop_percent=(
                float(item["boss_chest_drop_percent"])
                if item.get("boss_chest_drop_percent") is not None
                else None
            ),
        )
        for item in raw
    ]
    return tuple(
        sorted(
            entries,
            key=lambda item: (
                item.enemy_level,
                item.act,
                item.stage,
                DIFFICULTY_SORT_ORDER.get(item.difficulty, 99),
            ),
        )
    )


@lru_cache(maxsize=1)
def farmable_chest_levels() -> tuple[int, ...]:
    levels = sorted({entry.boss_chest_level for entry in load_stage_catalog()})
    return tuple(levels)


def find_catalog_entry(stage_key: int) -> StageCatalogEntry | None:
    for entry in load_stage_catalog():
        if entry.stage_key == stage_key:
            return entry
    return None


def stages_for_chest_level(chest_level: int) -> list[StageCatalogEntry]:
    return [
        entry
        for entry in load_stage_catalog()
        if entry.boss_chest_level == chest_level and not entry.is_act_boss
    ]


def suggested_stage_for_chest_level(chest_level: int) -> StageCatalogEntry | None:
    from src.data.chest_catalog import RECOMMENDED_FARM_PRESET

    preset = RECOMMENDED_FARM_PRESET.get(chest_level)
    if preset is not None:
        for entry in load_stage_catalog():
            if (
                entry.act == preset["act"]
                and entry.stage == preset["stage"]
                and entry.difficulty == preset["difficulty"]
            ):
                return entry

    candidates = stages_for_chest_level(chest_level)
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda item: (
            item.enemy_level,
            item.act,
            item.stage,
            DIFFICULTY_SORT_ORDER.get(item.difficulty, 99),
        ),
    )


def is_valid_map_for_chest_level(stage_key: int, chest_level: int) -> bool:
    entry = find_catalog_entry(stage_key)
    if entry is None:
        return False
    if entry.is_act_boss:
        return False
    return entry.boss_chest_level == chest_level


def boss_chest_level_for_key(item_key: str) -> int | None:
    for entry in load_stage_catalog():
        if entry.boss_chest_key == item_key:
            return entry.boss_chest_level
    from src.data.chest_catalog import load_boss_chest_catalog

    for item in load_boss_chest_catalog():
        if item.key == item_key:
            return item.level
    if item_key == "boss_box_data":
        return None
    return None


def boss_chest_level_for_stage_key(stage_key: int) -> int | None:
    entry = find_catalog_entry(stage_key)
    if entry is None:
        return None
    return entry.boss_chest_level


def boss_chest_drop_percent_for_stage_key(stage_key: int) -> float | None:
    entry = find_catalog_entry(stage_key)
    if entry is None:
        return None
    return entry.boss_chest_drop_percent


def merge_saved_maps(saved_maps: list[MapConfig]) -> list[MapConfig]:
    saved_by_key = {item.stage_key: item for item in saved_maps}
    merged: list[MapConfig] = []

    for index, entry in enumerate(load_stage_catalog(), start=1):
        saved = saved_by_key.get(entry.stage_key)
        if saved is not None:
            merged.append(saved)
            continue
        merged.append(entry.to_map_config(priority=1000 + index, enabled=False))

    return merged


def enabled_rotation_maps(all_maps: list[MapConfig]) -> list[MapConfig]:
    enabled = [item for item in all_maps if item.enabled]
    return sorted(enabled, key=lambda item: item.priority)


def maps_for_save(all_maps: list[MapConfig]) -> list[MapConfig]:
    return enabled_rotation_maps(all_maps)
