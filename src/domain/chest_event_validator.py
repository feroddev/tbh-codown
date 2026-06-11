from __future__ import annotations

from src.data.stage_catalog import find_catalog_entry
from src.domain.chest_event import ChestEvent, ChestType

GENERIC_SAVE_ITEM_KEYS = frozenset({"boss_box_data", "normal_box_data"})


def is_chest_event_consistent_with_stage(event: ChestEvent, stage_key: int) -> bool:
    if event.item_key in GENERIC_SAVE_ITEM_KEYS:
        return True

    if event.chest_type == ChestType.NORMAL_BROWN:
        return True

    entry = find_catalog_entry(stage_key)
    if entry is None:
        return True

    return event.item_key == entry.boss_chest_key
