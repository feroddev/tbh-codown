#!/usr/bin/env python3
"""Patch boss_chest_drop_percent for stages missing from wiki scrape."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES_JSON = ROOT / "src/data/stages.json"

# Act bosses: guaranteed boss chest on clear (wiki has no % line).
ACT_BOSS_DROP_PERCENT = 100.0

# Pharaoh's Crypt (2-9 Normal) — same tier as Sacred Tomb (2-8, 20%).
PHARAOH_CRYPT_NORMAL = 20.0


def main() -> None:
    stages = json.loads(STAGES_JSON.read_text(encoding="utf-8"))
    for entry in stages:
        if entry.get("boss_chest_drop_percent") is not None:
            continue
        if entry.get("is_act_boss"):
            entry["boss_chest_drop_percent"] = ACT_BOSS_DROP_PERCENT
            continue
        if (
            entry["difficulty"] == "Normal"
            and entry["act"] == 2
            and entry["stage"] == 9
            and entry["name"] == "Pharaoh's Crypt"
        ):
            entry["boss_chest_drop_percent"] = PHARAOH_CRYPT_NORMAL

    STAGES_JSON.write_text(
        json.dumps(stages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    missing = [e for e in stages if e.get("boss_chest_drop_percent") is None]
    print(f"Patched. Still missing: {len(missing)}")


if __name__ == "__main__":
    main()
