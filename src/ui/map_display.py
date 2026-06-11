from __future__ import annotations

from src.domain.rotation_engine import MapConfig


from src.ui.i18n import Language, format_act_stage, format_act_stage_arrow, localized_map_label, t


def game_stage_label(map_config: MapConfig, language: Language | None = None) -> str:
    return format_act_stage(
        map_config.act,
        map_config.stage,
        map_config.difficulty,
        language=language,
    )


def rotation_order_label(order: int, language: Language | None = None) -> str:
    return t("rotation_order", language=language, order=order)


def map_summary_line(map_config: MapConfig, order: int, language: Language | None = None) -> str:
    return (
        f"{rotation_order_label(order, language=language)} — "
        f"{game_stage_label(map_config, language=language)} — "
        f"{localized_map_label(map_config, language=language)}"
    )


def map_game_instruction(map_config: MapConfig, language: Language | None = None) -> str:
    return format_act_stage_arrow(
        map_config.act,
        map_config.stage,
        map_config.difficulty,
        language=language,
    )
