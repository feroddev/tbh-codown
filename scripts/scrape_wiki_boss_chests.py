#!/usr/bin/env python3
"""Scrape boss and common chest catalogs from taskbarherowiki.com item pages."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_RAW = ROOT / "src/data/wiki_boss_chests_raw.json"
CHESTS_JSON = ROOT / "src/data/boss_chests.json"
WEB_CHESTS_JSON = ROOT / "web-monitor/data/boss_chests.json"
COMMON_CHESTS_JSON = ROOT / "src/data/common_chests.json"
WEB_COMMON_CHESTS_JSON = ROOT / "web-monitor/data/common_chests.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DIFFICULTY_MAP = {
    "NORMAL": "Normal",
    "NIGHTMARE": "Nightmare",
    "HELL": "Hell",
    "TORMENT": "Torment",
}

STAGE_LINK = re.compile(
    r'href="/map\?diff=(\w+)&amp;stage=(\d+)-(\d+)"'
)
LEVEL_IN_NAME = re.compile(r"Lv(\d+)")
BOX_NUMBER = re.compile(r"Stage Boss Box (\d+)$")
NORMAL_BOX_NUMBER = re.compile(r"Normal Monster Box (\d+)$")
NO_LONGER_OBTAINABLE = "No longer obtainable"


def fetch_item_page(item_key: str) -> str:
    url = f"https://taskbarherowiki.com/items/{item_key}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_level_label(name: str, *, box_number_pattern: re.Pattern[str]) -> int:
    lv_match = LEVEL_IN_NAME.search(name)
    if lv_match:
        return int(lv_match.group(1))
    box_match = box_number_pattern.search(name)
    if box_match:
        return int(box_match.group(1))
    if name.endswith("Box 1"):
        return 1
    return 1


def parse_item_page(html: str, item_key: str) -> dict | None:
    if "404" in html and "Not Found" in html:
        return None

    name_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    if not name_match:
        return None
    name = name_match.group(1).strip()
    box_number_pattern = (
        NORMAL_BOX_NUMBER if item_key.startswith("91") else BOX_NUMBER
    )
    level_label = parse_level_label(name, box_number_pattern=box_number_pattern)

    stages: list[dict] = []
    seen_stages: set[tuple[int, int, str]] = set()
    for diff, act, stage in STAGE_LINK.findall(html):
        difficulty = DIFFICULTY_MAP.get(diff, diff)
        stage_key = (int(act), int(stage), difficulty)
        if stage_key in seen_stages:
            continue
        seen_stages.add(stage_key)
        stages.append(
            {
                "act": stage_key[0],
                "stage": stage_key[1],
                "difficulty": stage_key[2],
            }
        )

    return {
        "key": item_key,
        "name": name,
        "level": level_label,
        "level_label": level_label,
        "stages": stages,
        "obtainable": NO_LONGER_OBTAINABLE not in html,
    }


def discover_item_keys() -> list[str]:
    """Known boss chest keys from wiki (stage + act families)."""
    keys: list[str] = ["920001", "920011", "920051", "920101"]
    keys.extend(f"920{level}1" for level in range(15, 95, 5))
    keys.extend(
        [
            "930101",
            "930401",
            "930501",
            "930651",
            "930701",
            "930851",
            "930901",
        ]
    )
    return sorted(set(keys))


def is_droppable_boss(chest: dict) -> bool:
    return bool(chest.get("stages")) and chest.get("obtainable", True)


def build_boss_catalog(wiki_raw: list[dict]) -> list[dict]:
    catalog: list[dict] = []
    seen: set[str] = set()
    for chest in wiki_raw:
        if not is_droppable_boss(chest):
            continue
        key = chest["key"]
        if key in seen:
            continue
        seen.add(key)
        catalog.append(
            {
                "key": key,
                "label": chest["name"],
                "level": chest["level_label"],
            }
        )
    catalog.sort(key=lambda item: (item["level"], item["key"]))
    return catalog


def common_key_for_boss_key(boss_key: str) -> str | None:
    if not boss_key.startswith("92") or len(boss_key) < 6:
        return None
    return f"91{boss_key[2:]}"


def discover_common_keys(boss_catalog: list[dict]) -> list[str]:
    keys: list[str] = []
    for chest in boss_catalog:
        common_key = common_key_for_boss_key(chest["key"])
        if common_key is not None:
            keys.append(common_key)
    return sorted(set(keys))


def build_common_catalog(
    common_keys: list[str],
    boss_catalog: list[dict],
    *,
    sleep_seconds: float = 0.35,
) -> list[dict]:
    boss_level_by_common_key = {
        common_key: chest["level"]
        for chest in boss_catalog
        if (common_key := common_key_for_boss_key(chest["key"])) is not None
    }
    catalog: list[dict] = []
    missing: list[str] = []

    for index, key in enumerate(common_keys):
        try:
            html = fetch_item_page(key)
            parsed = parse_item_page(html, key)
            if parsed is None or not parsed.get("obtainable", True):
                missing.append(key)
                print(f"[common {index + 1}/{len(common_keys)}] {key} -> skipped")
                continue
            catalog.append(
                {
                    "key": parsed["key"],
                    "label": parsed["name"],
                    "level": boss_level_by_common_key.get(
                        parsed["key"],
                        parsed["level_label"],
                    ),
                }
            )
            print(
                f"[common {index + 1}/{len(common_keys)}] {key} -> {parsed['name']}"
            )
        except urllib.error.HTTPError as error:
            if error.code == 404:
                missing.append(key)
                print(f"[common {index + 1}/{len(common_keys)}] {key} -> 404")
            else:
                raise
        if index + 1 < len(common_keys):
            time.sleep(sleep_seconds)

    catalog.sort(key=lambda item: (item["level"], item["key"]))
    if missing:
        print(f"Common skipped/404: {', '.join(missing)}")
    return catalog


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def publish_catalogs(
    boss_catalog: list[dict],
    common_catalog: list[dict],
) -> None:
    write_json(CHESTS_JSON, boss_catalog)
    write_json(WEB_CHESTS_JSON, boss_catalog)
    write_json(COMMON_CHESTS_JSON, common_catalog)
    write_json(WEB_COMMON_CHESTS_JSON, common_catalog)


def main() -> None:
    keys = discover_item_keys()
    wiki_raw: list[dict] = []
    missing: list[str] = []

    for index, key in enumerate(keys):
        try:
            html = fetch_item_page(key)
            parsed = parse_item_page(html, key)
            if parsed is None:
                missing.append(key)
                continue
            wiki_raw.append(parsed)
            droppable = "droppable" if is_droppable_boss(parsed) else "legacy"
            print(
                f"[boss {index + 1}/{len(keys)}] {key} -> {parsed['name']} "
                f"({len(parsed['stages'])} stages, {droppable})"
            )
        except urllib.error.HTTPError as error:
            if error.code == 404:
                missing.append(key)
                print(f"[boss {index + 1}/{len(keys)}] {key} -> 404")
            else:
                raise
        if index + 1 < len(keys):
            time.sleep(0.35)

    wiki_raw.sort(key=lambda item: (item["level_label"], item["key"]))
    write_json(WIKI_RAW, wiki_raw)

    boss_catalog = build_boss_catalog(wiki_raw)
    common_catalog = build_common_catalog(
        discover_common_keys(boss_catalog),
        boss_catalog,
    )
    publish_catalogs(boss_catalog, common_catalog)

    print(f"\nUpdated {WIKI_RAW.name} ({len(wiki_raw)} wiki entries)")
    print(
        f"Published {len(boss_catalog)} droppable boss chests and "
        f"{len(common_catalog)} common chests"
    )
    if missing:
        print(f"Boss missing/404: {', '.join(missing)}")


if __name__ == "__main__":
    main()
