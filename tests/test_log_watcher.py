from __future__ import annotations

import unittest

from src.domain.chest_event import ChestEvent, ChestType
from src.infrastructure.log_watcher import ChestDetector, is_inventory_sync_burst


class LogWatcherTests(unittest.TestCase):
    def test_detector_fires_on_repeated_count_one_lines(self) -> None:
        detector = ChestDetector(consider_common_chest=True, debounce_seconds=0.0)
        line = "GetBoxCount Success Count : 1 // ItemKey : 920651"

        first = detector.process_line(line)
        second = detector.process_line(line)

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertEqual(first.item_key, "920651")

    def test_inventory_burst_is_filtered(self) -> None:
        events = [
            ChestEvent("920301", ChestType.BOSS, 1, ""),
            ChestEvent("920401", ChestType.BOSS, 1, ""),
            ChestEvent("920501", ChestType.BOSS, 1, ""),
        ]
        self.assertTrue(is_inventory_sync_burst(events))

    def test_single_drop_is_not_burst(self) -> None:
        events = [
            ChestEvent("920651", ChestType.BOSS, 1, ""),
        ]
        self.assertFalse(is_inventory_sync_burst(events))


if __name__ == "__main__":
    unittest.main()
