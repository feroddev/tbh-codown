from __future__ import annotations

import time
import unittest

from src.domain.chest_drop_correlator import ChestDropCorrelator
from src.domain.chest_event import ChestEvent, ChestType


class ChestDropCorrelatorTests(unittest.TestCase):
    def test_log_drop_confirms_immediately_for_boss(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=12.0)
        event = ChestEvent("920401", ChestType.BOSS, 2, "log")

        confirmed = correlator.register_log_drop(event, stage_key=2201)

        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0].stage_key, 2201)
        self.assertEqual(confirmed[0].event.item_key, "920401")

    def test_save_drop_suppressed_after_recent_log_confirm(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=12.0)
        log_event = ChestEvent("920401", ChestType.BOSS, 2, "log")
        save_event = ChestEvent("boss_box_data", ChestType.BOSS, 2, "save")

        correlator.register_log_drop(log_event, stage_key=2201)
        suppressed = correlator.register_save_drop(save_event, stage_key=2201)

        self.assertEqual(suppressed, [])

    def test_save_drop_confirms_when_log_did_not(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=12.0)
        save_event = ChestEvent("boss_box_data", ChestType.BOSS, 3, "save")

        confirmed = correlator.register_save_drop(save_event, stage_key=2201)

        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0].event.item_key, "boss_box_data")

    def test_save_drop_allowed_after_suppress_window(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=0.01)
        log_event = ChestEvent("920401", ChestType.BOSS, 2, "log")
        save_event = ChestEvent("boss_box_data", ChestType.BOSS, 2, "save")

        correlator.register_log_drop(log_event, stage_key=2201)
        time.sleep(0.02)
        confirmed = correlator.register_save_drop(save_event, stage_key=2201)

        self.assertEqual(len(confirmed), 1)

    def test_log_drop_suppressed_after_recent_save_confirm(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=12.0)
        save_event = ChestEvent("normal_box_data", ChestType.NORMAL_BROWN, 2, "save")
        log_event = ChestEvent("910501", ChestType.NORMAL_BROWN, 2, "log")

        correlator.register_save_drop(save_event, stage_key=2201)
        suppressed = correlator.register_log_drop(log_event, stage_key=2201)

        self.assertEqual(suppressed, [])

    def test_duplicate_log_drop_suppressed(self) -> None:
        correlator = ChestDropCorrelator(log_save_suppress_seconds=12.0)
        log_event = ChestEvent("910501", ChestType.NORMAL_BROWN, 2, "log")

        correlator.register_log_drop(log_event, stage_key=2201)
        suppressed = correlator.register_log_drop(log_event, stage_key=2201)

        self.assertEqual(suppressed, [])


if __name__ == "__main__":
    unittest.main()
