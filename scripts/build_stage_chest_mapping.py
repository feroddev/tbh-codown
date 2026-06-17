#!/usr/bin/env python3
"""Build stage boss chest mapping from taskbarherowiki.com scraped data."""

from __future__ import annotations

import json
from pathlib import Path

from src.data.stage_codec import Difficulty, encode_stage_key

ROOT = Path(__file__).resolve().parents[1]
WIKI_RAW = ROOT / "src/data/wiki_boss_chests_raw.json"
STAGES_JSON = ROOT / "src/data/stages.json"
WEB_STAGES_JSON = ROOT / "web-monitor/data/stages.json"
CHESTS_JSON = ROOT / "src/data/boss_chests.json"

DIFF_ORDER = ["Normal", "Nightmare", "Hell", "Torment"]

# Fill gaps for stages missing from wiki (act bosses, transitional tiers).
# Source: taskbarherowiki.com + taskbarhero.org item-level gates.
MANUAL_OVERRIDES: dict[tuple[int, int, str], tuple[str, int, str]] = {
    # (act, stage, difficulty): (item_key, display_level, name)
    (1, 10, "Normal"): ("920101", 7, "Stage Boss Box 7"),
    (2, 10, "Normal"): ("920201", 20, "Stage Boss Box Lv20"),
    (3, 10, "Normal"): ("920301", 30, "Stage Boss Box Lv30"),
    (1, 10, "Nightmare"): ("920401", 40, "Stage Boss Box Lv40"),
    (2, 10, "Nightmare"): ("920401", 40, "Stage Boss Box Lv40"),
    (3, 10, "Nightmare"): ("920501", 50, "Stage Boss Box Lv50"),
    (1, 10, "Hell"): ("920501", 50, "Stage Boss Box Lv50"),
    (2, 10, "Hell"): ("920501", 50, "Stage Boss Box Lv50"),
    (3, 10, "Hell"): ("920651", 65, "Stage Boss Box Lv65"),
    (1, 10, "Torment"): ("920651", 65, "Stage Boss Box Lv65"),
    (2, 10, "Torment"): ("920801", 80, "Stage Boss Box Lv80"),
    (3, 10, "Torment"): ("920801", 80, "Stage Boss Box Lv80"),
}


def stage_tuple(entry: dict) -> tuple[int, int, str]:
    return (int(entry["act"]), int(entry["stage"]), str(entry["difficulty"]))


def build_inverse_map(wiki_raw: list[dict]) -> dict[tuple[int, int, str], dict]:
    mapping: dict[tuple[int, int, str], dict] = {}
    for chest in wiki_raw:
        for stage in chest.get("stages", []):
            key = (int(stage["act"]), int(stage["stage"]), str(stage["difficulty"]))
            mapping[key] = {
                "boss_chest_key": chest["key"],
                "boss_chest_level": chest["level_label"],
                "boss_chest_name": chest["name"],
            }
    for override_key, (item_key, level, name) in MANUAL_OVERRIDES.items():
        if override_key not in mapping:
            mapping[override_key] = {
                "boss_chest_key": item_key,
                "boss_chest_level": level,
                "boss_chest_name": name,
            }
    return mapping


def infer_missing(mapping: dict[tuple[int, int, str], dict]) -> None:
    """Infer chest for stages still unmapped within same act/difficulty progression."""
    stages = json.loads(STAGES_JSON.read_text(encoding="utf-8"))
    grouped: dict[tuple[str, int], list[dict]] = {}
    for entry in stages:
        grouped.setdefault((entry["difficulty"], int(entry["act"])), []).append(entry)

    for (_difficulty, _act), entries in grouped.items():
        entries.sort(key=lambda item: int(item["stage"]))
        last: dict | None = None
        for entry in entries:
            key = stage_tuple(entry)
            if key in mapping:
                last = mapping[key]
                continue
            if last is not None:
                mapping[key] = dict(last)


def build_boss_chest_catalog(wiki_raw: list[dict]) -> list[dict]:
    catalog: list[dict] = []
    seen: set[str] = set()
    for chest in wiki_raw:
        if not chest.get("stages"):
            continue
        if chest["key"] in seen:
            continue
        seen.add(chest["key"])
        catalog.append(
            {
                "key": chest["key"],
                "label": chest["name"],
                "level": chest["level_label"],
            }
        )
    catalog.sort(key=lambda item: (item["level"], item["key"]))
    return catalog


def main() -> None:
    wiki_raw = json.loads(WIKI_RAW.read_text(encoding="utf-8"))
    mapping = build_inverse_map(wiki_raw)
    infer_missing(mapping)

    stages = json.loads(STAGES_JSON.read_text(encoding="utf-8"))
    unmapped: list[str] = []
    for entry in stages:
        key = stage_tuple(entry)
        chest = mapping.get(key)
        if chest is None:
            unmapped.append(f"{entry['difficulty']} {entry['act']}-{entry['stage']}")
            continue
        entry["boss_chest_key"] = chest["boss_chest_key"]
        entry["boss_chest_level"] = chest["boss_chest_level"]
        entry["boss_chest_name"] = chest["boss_chest_name"]

    stages_payload = json.dumps(stages, indent=2, ensure_ascii=False) + "\n"
    STAGES_JSON.write_text(stages_payload, encoding="utf-8")
    WEB_STAGES_JSON.write_text(stages_payload, encoding="utf-8")
    CHESTS_JSON.write_text(
        json.dumps(build_boss_chest_catalog(wiki_raw), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    WEB_CHESTS_JSON = ROOT / "web-monitor/data/boss_chests.json"
    WEB_CHESTS_JSON.write_text(
        json.dumps(build_boss_chest_catalog(wiki_raw), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated {STAGES_JSON.name} and {WEB_STAGES_JSON.name} ({len(stages)} stages)")
    print(f"Unmapped: {len(unmapped)}")
    if unmapped:
        print("  ", ", ".join(unmapped[:20]))


if __name__ == "__main__":
    main()
