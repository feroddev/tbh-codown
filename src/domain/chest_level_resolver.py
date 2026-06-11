from __future__ import annotations

from src.data.stage_catalog import boss_chest_level_for_key, boss_chest_level_for_stage_key
from src.domain.chest_event import ChestEvent, ChestType


def drop_chest_level_for_event(event: ChestEvent, stage_key: int) -> int | None:
    stage_level = boss_chest_level_for_stage_key(stage_key)

    if event.chest_type == ChestType.NORMAL_BROWN:
        return stage_level

    if event.item_key not in {"boss_box_data", "normal_box_data"}:
        key_level = boss_chest_level_for_key(event.item_key)
        if key_level is not None:
            return key_level

    return stage_level
