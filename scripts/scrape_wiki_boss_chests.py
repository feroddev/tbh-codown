#!/usr/bin/env python3
"""Scrape boss chest catalog from taskbarherowiki.com item pages."""

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


def fetch_item_page(item_key: str) -> str:
    url = f"https://taskbarherowiki.com/items/{item_key}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_item_page(html: str, item_key: str) -> dict | None:
    if "404" in html and "Not Found" in html:
        return None

    name_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    if not name_match:
        return None
    name = name_match.group(1).strip()

    level_label = 1
    lv_match = LEVEL_IN_NAME.search(name)
    if lv_match:
        level_label = int(lv_match.group(1))
    else:
        box_match = BOX_NUMBER.search(name)
        if box_match:
            level_label = int(box_match.group(1))
        elif name.endswith("Box 1"):
            level_label = 1

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
            "930851",
            "930901",
        ]
    )
    return sorted(set(keys))


def build_catalog(wiki_raw: list[dict]) -> list[dict]:
    catalog: list[dict] = []
    seen: set[str] = set()
    for chest in wiki_raw:
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
            print(f"[{index + 1}/{len(keys)}] {key} -> {parsed['name']} ({len(parsed['stages'])} stages)")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                missing.append(key)
                print(f"[{index + 1}/{len(keys)}] {key} -> 404")
            else:
                raise
        if index + 1 < len(keys):
            time.sleep(0.35)

    wiki_raw.sort(key=lambda item: (item["level_label"], item["key"]))
    WIKI_RAW.write_text(
        json.dumps(wiki_raw, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    catalog = build_catalog(wiki_raw)
    payload = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    CHESTS_JSON.write_text(payload, encoding="utf-8")
    WEB_CHESTS_JSON.write_text(payload, encoding="utf-8")

    print(f"\nUpdated {WIKI_RAW.name} ({len(wiki_raw)} chests)")
    print(f"Updated {CHESTS_JSON.name} and {WEB_CHESTS_JSON.name}")
    if missing:
        print(f"Missing/404: {', '.join(missing)}")


if __name__ == "__main__":
    main()
