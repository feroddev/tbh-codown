from src.data.stage_catalog import (
    is_valid_map_for_chest_level,
    load_stage_catalog,
    stages_for_chest_level,
)


def test_stages_for_chest_level_excludes_act_boss_maps() -> None:
    for chest_level in {entry.boss_chest_level for entry in load_stage_catalog()}:
        stages = stages_for_chest_level(chest_level)
        assert stages
        assert all(not entry.is_act_boss for entry in stages)
        assert all(entry.stage != 10 for entry in stages)


def test_is_valid_map_for_chest_level_rejects_act_boss() -> None:
    act_boss = next(entry for entry in load_stage_catalog() if entry.is_act_boss)
    assert not is_valid_map_for_chest_level(act_boss.stage_key, act_boss.boss_chest_level)
