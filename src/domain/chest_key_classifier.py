from __future__ import annotations

from functools import lru_cache

from src.data.chest_catalog import load_boss_chest_catalog, normal_brown_item_keys
from src.domain.chest_event import ChestType


@lru_cache(maxsize=1)
def stage_boss_item_keys() -> frozenset[str]:
    return frozenset(item.key for item in load_boss_chest_catalog())


def is_stage_boss_item_key(item_key: str) -> bool:
    return item_key in stage_boss_item_keys()


def is_boss_chest_key(item_key: str) -> bool:
    return is_stage_boss_item_key(item_key)


def is_common_chest_item_key(item_key: str) -> bool:
    if is_stage_boss_item_key(item_key):
        return False
    return item_key in normal_brown_item_keys() or item_key.startswith("910")


def classify_chest_item_key(item_key: str, *, consider_common_chest: bool) -> ChestType | None:
    if is_stage_boss_item_key(item_key):
        return ChestType.BOSS
    if consider_common_chest and is_common_chest_item_key(item_key):
        return ChestType.NORMAL_BROWN
    return None