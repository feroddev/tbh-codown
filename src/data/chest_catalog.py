from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.domain.rotation_engine import MapConfig
from src.ui.i18n import Language, format_chest_level_label

CHESTS_JSON = Path(__file__).with_name("boss_chests.json")


@dataclass(frozen=True)
class BossChestDefinition:
    key: str
    label: str
    level: int
    obtainable: bool = True


@lru_cache(maxsize=1)
def load_boss_chest_catalog() -> tuple[BossChestDefinition, ...]:
    raw = json.loads(CHESTS_JSON.read_text(encoding="utf-8"))
    stages = json.loads(Path(__file__).with_name("stages.json").read_text(encoding="utf-8"))
    active_levels = {int(item["boss_chest_level"]) for item in stages}
    items = [
        BossChestDefinition(
            key=str(entry["key"]),
            label=str(entry["label"]),
            level=int(entry["level"]),
            obtainable=int(entry["level"]) in active_levels,
        )
        for entry in raw
    ]
    return tuple(items)


BOSS_CHEST_CATALOG: list[BossChestDefinition] = []  # populated on import below


def _init_catalog() -> None:
    global BOSS_CHEST_CATALOG
    BOSS_CHEST_CATALOG = list(load_boss_chest_catalog())


NORMAL_CHEST_CATALOG: list[BossChestDefinition] = [
    BossChestDefinition("910301", "Normal Monster Box Lv1", 1),
    BossChestDefinition("910351", "Normal Monster Box Lv2", 2),
    BossChestDefinition("920301", "Normal Monster Box Lv1", 1),
    BossChestDefinition("920351", "Normal Monster Box Lv2", 2),
    BossChestDefinition("920371", "Normal Monster Box Lv3", 3),
    BossChestDefinition("920381", "Normal Monster Box Lv4", 4),
    BossChestDefinition("920391", "Normal Monster Box Lv5", 5),
]

RECOMMENDED_FARM_PRESET: dict[int, dict[str, object]] = {
    4: {
        "label": "1-1 Pasture (Normal)",
        "act": 1,
        "stage": 1,
        "difficulty": "Normal",
        "boss_key": "920011",
        "reason": "Primeiro mapa; dropa Stage Boss Box 4 (wiki).",
    },
    5: {
        "label": "1-4 Eerie Canyon (Normal)",
        "act": 1,
        "stage": 4,
        "difficulty": "Normal",
        "boss_key": "920051",
        "reason": "Stage Boss Box 5 — wiki.",
    },
    7: {
        "label": "1-8 Cemetery (Normal)",
        "act": 1,
        "stage": 8,
        "difficulty": "Normal",
        "boss_key": "920101",
        "reason": "Stage Boss Box 7 — wiki.",
    },
    15: {
        "label": "2-3 Desert Underground Cave (Normal)",
        "act": 2,
        "stage": 3,
        "difficulty": "Normal",
        "boss_key": "920151",
        "reason": "Stage Boss Box Lv15 — wiki.",
    },
    20: {
        "label": "2-8 Sacred Tomb (Normal)",
        "act": 2,
        "stage": 8,
        "difficulty": "Normal",
        "boss_key": "920201",
        "reason": "Stage Boss Box Lv20 — wiki.",
    },
    30: {
        "label": "3-8 Citadel of Ruin (Normal)",
        "act": 3,
        "stage": 8,
        "difficulty": "Normal",
        "boss_key": "920301",
        "reason": "Stage Boss Box Lv30 — wiki.",
    },
    40: {
        "label": "1-9 Cursed Land (Nightmare)",
        "act": 1,
        "stage": 9,
        "difficulty": "Nightmare",
        "boss_key": "920401",
        "reason": "15% boss drop no Pesadelo (wiki); menor HP entre mapas Lv40.",
    },
    50: {
        "label": "3-5 Hell Gate (Nightmare)",
        "act": 3,
        "stage": 5,
        "difficulty": "Nightmare",
        "boss_key": "920501",
        "reason": "15% boss drop no Pesadelo (wiki); Inferno cai 10%.",
    },
    65: {
        "label": "2-5 Scorching Dunes (Hell)",
        "act": 2,
        "stage": 5,
        "difficulty": "Hell",
        "boss_key": "920651",
        "reason": "10% boss drop no Inferno (wiki); Torment cai 8%.",
    },
    80: {
        "label": "1-3 Wasteland (Torment)",
        "act": 1,
        "stage": 3,
        "difficulty": "Torment",
        "boss_key": "920801",
        "reason": "8% boss drop na Torment (wiki); mesma % do 2-1 com menor HP entre mapas Lv80.",
    },
}


def catalog_keys(catalog: list[BossChestDefinition]) -> list[str]:
    return [item.key for item in catalog]


def catalog_label_for_key(key: str) -> str:
    for item in (*load_boss_chest_catalog(), *NORMAL_CHEST_CATALOG):
        if item.key == key:
            return item.label
    return key


def normal_brown_item_keys() -> frozenset[str]:
    boss_keys = {item.key for item in load_boss_chest_catalog()}
    return frozenset(
        item.key for item in NORMAL_CHEST_CATALOG if item.key not in boss_keys
    )


def common_chest_level_for_key(item_key: str) -> int | None:
    if item_key == "normal_box_data":
        return None
    for item in NORMAL_CHEST_CATALOG:
        if item.key == item_key:
            return item.level
    return None


def boss_farm_levels() -> tuple[int, ...]:
    stages = json.loads(Path(__file__).with_name("stages.json").read_text(encoding="utf-8"))
    return tuple(sorted({int(item["boss_chest_level"]) for item in stages}))


def boss_key_for_level(level: int) -> str | None:
    for item in load_boss_chest_catalog():
        if item.level == level:
            return item.key
    return None


def boss_chest_for_map(map_config: MapConfig) -> BossChestDefinition | None:
    if map_config.boss_chest_keys:
        key = map_config.boss_chest_keys[0]
        for item in load_boss_chest_catalog():
            if item.key == key:
                return item

    for preset in RECOMMENDED_FARM_PRESET.values():
        if (
            preset["act"] == map_config.act
            and preset["stage"] == map_config.stage
            and preset["difficulty"] == map_config.difficulty
        ):
            for item in load_boss_chest_catalog():
                if item.key == preset["boss_key"]:
                    return item

    level_match = re.search(r"Lv\s*(\d+)", map_config.label, flags=re.IGNORECASE)
    if level_match:
        target_level = int(level_match.group(1))
        for item in load_boss_chest_catalog():
            if item.level == target_level:
                return item

    return None


def boss_chest_summary(map_config: MapConfig) -> str:
    chest = boss_chest_for_map(map_config)
    if chest is None:
        return "Baú de chefe não identificado"
    return f"Baú deste mapa: {chest.label}"


def chest_display_label(
    level: int,
    language: Language | str | None = None,
    *,
    short: bool = False,
) -> str:
    from src.ui.i18n import t

    if isinstance(language, str):
        language = Language.from_code(language)
    key = f"chest_name_short_{level}" if short else f"chest_name_{level}"
    translated = t(key, language=language)
    if translated != key:
        return translated
    for item in load_boss_chest_catalog():
        if item.level == level:
            return item.label
    return format_chest_level_label(level, language=language)


_init_catalog()
