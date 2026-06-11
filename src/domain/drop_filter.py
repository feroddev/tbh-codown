from __future__ import annotations

from dataclasses import dataclass

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.rotation_engine import MapConfig
from src.ui.i18n import Language, t


@dataclass(frozen=True)
class StrategySettings:
    consider_common_chest: bool = False


def should_rotate_on_drop(
    event: ChestEvent,
    current_map: MapConfig,
    strategy: StrategySettings,
    language: Language | None = None,
) -> tuple[bool, str]:
    if event.chest_type == ChestType.NORMAL_BROWN:
        if not strategy.consider_common_chest:
            return False, t("drop_reason_common_ignored", language=language)
        return False, t("drop_reason_common_no_rotation", language=language)

    if event.chest_type == ChestType.BOSS:
        if event.item_key == "boss_box_data":
            return True, t("drop_reason_boss_detected", language=language)
        if current_map.boss_chest_keys and event.item_key not in current_map.boss_chest_keys:
            return False, t(
                "drop_reason_boss_not_monitored",
                language=language,
                item_key=event.item_key,
            )

    return True, t("drop_reason_valid", language=language)
