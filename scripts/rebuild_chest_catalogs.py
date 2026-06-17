#!/usr/bin/env python3
"""Rebuild chest catalogs from cached wiki boss data (no boss re-scrape)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scrape_wiki_boss_chests import (  # noqa: E402
    WIKI_RAW,
    build_boss_catalog,
    build_common_catalog,
    discover_common_keys,
    publish_catalogs,
)


def main() -> None:
    wiki_raw = json.loads(WIKI_RAW.read_text(encoding="utf-8"))
    boss_catalog = build_boss_catalog(wiki_raw)
    common_catalog = build_common_catalog(
        discover_common_keys(boss_catalog),
        boss_catalog,
    )
    publish_catalogs(boss_catalog, common_catalog)
    print(f"Rebuilt {len(boss_catalog)} boss and {len(common_catalog)} common chests")


if __name__ == "__main__":
    main()
