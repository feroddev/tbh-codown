from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.domain.chest_event import ChestEvent, ChestType
from src.infrastructure.log_watcher import (
    ChestDetector,
    PlayerLogPoller,
    filter_inventory_sync_burst,
    is_inventory_sync_burst,
)


class LogWatcherTests(unittest.TestCase):
    def test_count_tracking_baselines_first_line_without_emitting(self) -> None:
        detector = ChestDetector(consider_common_chest=True, debounce_seconds=4.0)
        detector.enable_count_tracking(True)
        line = "GetBoxCount Success Count : 1 // ItemKey : 920301"

        first = detector.process_line(line)
        second = detector.process_line(line)

        self.assertIsNone(first)
        self.assertIsNone(second)

    def test_watch_boss_key_emits_first_sight_count_one(self) -> None:
        detector = ChestDetector(
            consider_common_chest=True,
            debounce_seconds=4.0,
            watch_boss_keys=frozenset({"920401"}),
        )
        detector.enable_count_tracking(True)

        event = detector.process_line(
            "GetBoxCount Success Count : 1 // ItemKey : 920401"
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.count, 1)

    def test_count_tracking_updates_baseline_when_chest_is_opened(self) -> None:
        detector = ChestDetector(consider_common_chest=True, debounce_seconds=4.0)
        detector.enable_count_tracking(True)

        detector.process_line("GetBoxCount Success Count : 3 // ItemKey : 920301")
        opened = detector.process_line(
            "GetBoxCount Success Count : 2 // ItemKey : 920301"
        )
        sync = detector.process_line(
            "GetBoxCount Success Count : 2 // ItemKey : 920301"
        )
        new_drop = detector.process_line(
            "GetBoxCount Success Count : 3 // ItemKey : 920301"
        )

        self.assertIsNone(opened)
        self.assertIsNone(sync)
        self.assertIsNotNone(new_drop)
        self.assertEqual(new_drop.count, 3)

    def test_count_tracking_detects_inventory_increase(self) -> None:
        detector = ChestDetector(consider_common_chest=True, debounce_seconds=4.0)
        detector.enable_count_tracking(True)

        detector.seed_line("GetBoxCount Success Count : 1 // ItemKey : 920301")
        increased = detector.process_line(
            "GetBoxCount Success Count : 2 // ItemKey : 920301"
        )

        self.assertIsNotNone(increased)
        self.assertEqual(increased.count, 2)

    def test_inventory_burst_is_filtered(self) -> None:
        events = [
            ChestEvent("920301", ChestType.BOSS, 1, ""),
            ChestEvent("920401", ChestType.BOSS, 1, ""),
            ChestEvent("920501", ChestType.BOSS, 1, ""),
        ]
        self.assertTrue(is_inventory_sync_burst(events))
        self.assertEqual(filter_inventory_sync_burst(events), [])

    def test_inventory_burst_preserves_current_map_boss_key(self) -> None:
        events = [
            ChestEvent("920301", ChestType.BOSS, 1, ""),
            ChestEvent("920401", ChestType.BOSS, 1, ""),
            ChestEvent("920501", ChestType.BOSS, 1, ""),
        ]

        filtered = filter_inventory_sync_burst(
            events,
            preserve_item_keys=frozenset({"920401"}),
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].item_key, "920401")

    def test_seed_from_log_tail_sets_baseline_without_emitting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "Player.log"
            log_path.write_text(
                "\n".join(
                    [
                        "GetBoxCount Success Count : 1 // ItemKey : 920401",
                        "GetBoxCount Success Count : 2 // ItemKey : 920651",
                    ]
                ),
                encoding="utf-8",
            )

            poller = PlayerLogPoller(
                log_path,
                consider_common_chest=True,
                watch_boss_keys=frozenset({"920401"}),
            )
            poller.seed_from_log_tail()

            event = poller._detector.process_line(
                "GetBoxCount Success Count : 2 // ItemKey : 920401"
            )

            self.assertIsNotNone(event)
            self.assertEqual(event.count, 2)


if __name__ == "__main__":
    unittest.main()
