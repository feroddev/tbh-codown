from __future__ import annotations

import unittest
from datetime import datetime

from src.ui.i18n import Language, format_chest_drop_log


class FormatChestDropLogTests(unittest.TestCase):
    def test_boss_drop_includes_time_kind_level_and_map(self) -> None:
        message = format_chest_drop_log(
            chest_level=65,
            stage_key=3205,
            chest_kind="Chefe",
            language=Language.PT_BR,
            dropped_at=datetime(2026, 6, 15, 12, 34, 56),
        )

        self.assertEqual(message, "12:34:56 · Chefe · Lv65 · 10% - 2-5 · Inferno")

    def test_common_drop_includes_map_label_in_english(self) -> None:
        message = format_chest_drop_log(
            chest_level=50,
            stage_key=2305,
            chest_kind="Common",
            language=Language.EN,
            dropped_at=datetime(2026, 6, 15, 17, 0, 0),
        )

        self.assertEqual(message, "17:00:00 · Common · Lv50 · 15% - 3-5 · Nightmare")


if __name__ == "__main__":
    unittest.main()
