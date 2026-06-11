from src.data.boss_chest_drop_rate import format_boss_drop_percent
from src.data.stage_catalog import suggested_stage_for_chest_level
from src.ui.i18n import Language, format_map_drop_label, format_watch_map_label


def test_format_boss_drop_percent_integers() -> None:
    assert format_boss_drop_percent(15.0) == "15%"
    assert format_boss_drop_percent(100.0) == "100%"


def test_format_map_drop_label_prefixes_boss_rate() -> None:
    label = format_map_drop_label(
        act=3,
        stage=5,
        map_name="Hell Gate",
        boss_drop_percent=15.0,
        language=Language.EN,
    )
    assert label == "15% 3.5 Hell Gate"


def test_suggested_lv50_map_label_includes_nightmare_drop_rate() -> None:
    entry = suggested_stage_for_chest_level(50)
    assert entry is not None
    assert entry.boss_chest_drop_percent == 15.0
    label = format_watch_map_label(
        act=entry.act,
        stage=entry.stage,
        difficulty=entry.difficulty,
        map_name=entry.name,
        boss_drop_percent=entry.boss_chest_drop_percent,
        language=Language.PT_BR,
    )
    assert label.startswith("15% 3.5 ")
