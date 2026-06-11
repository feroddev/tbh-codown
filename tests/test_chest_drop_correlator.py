from __future__ import annotations

import time
import unittest

from src.domain.chest_drop_correlator import ChestDropCorrelator
from src.domain.chest_event import ChestEvent, ChestType


def _boss_log_event(item_key: str = "920651") -> ChestEvent:
    return ChestEvent(
        item_key=item_key,
        chest_type=ChestType.BOSS,
        count=1,
        raw_line=f"GetBoxCount Success Count : 1 // ItemKey : {item_key}",
    )


def _save_boss_event() -> ChestEvent:
    return ChestEvent(
        item_key="boss_box_data",
        chest_type=ChestType.BOSS,
        count=2,
        raw_line="save boss increase",
    )


class ChestDropCorrelatorTests(unittest.TestCase):
    def test_save_then_log_emits_once_with_log_item_key(self) -> None:
        correlator = ChestDropCorrelator(confirmation_window_seconds=15.0)

        save_results = correlator.register_save_drop(_save_boss_event(), stage_key=3205)
        self.assertEqual(save_results, [])

        log_results = correlator.register_log_drop(_boss_log_event(), stage_key=3205)
        self.assertEqual(len(log_results), 1)
        self.assertEqual(log_results[0].event.item_key, "920651")
        self.assertEqual(log_results[0].stage_key, 3205)

    def test_log_then_save_emits_once(self) -> None:
        correlator = ChestDropCorrelator(confirmation_window_seconds=15.0)

        log_results = correlator.register_log_drop(_boss_log_event(), stage_key=3205)
        self.assertEqual(log_results, [])

        save_results = correlator.register_save_drop(_save_boss_event(), stage_key=3205)
        self.assertEqual(len(save_results), 1)
        self.assertEqual(save_results[0].event.item_key, "920651")

    def test_mismatched_stage_does_not_confirm(self) -> None:
        correlator = ChestDropCorrelator(confirmation_window_seconds=15.0)

        correlator.register_save_drop(_save_boss_event(), stage_key=3205)
        log_results = correlator.register_log_drop(_boss_log_event("920301"), stage_key=1308)

        self.assertEqual(log_results, [])
        self.assertEqual(len(correlator.collect_save_fallbacks()), 0)

    def test_save_fallback_after_confirmation_window(self) -> None:
        correlator = ChestDropCorrelator(confirmation_window_seconds=0.05)

        correlator.register_save_drop(_save_boss_event(), stage_key=3205)
        time.sleep(0.06)

        fallbacks = correlator.collect_save_fallbacks()
        self.assertEqual(len(fallbacks), 1)
        self.assertEqual(fallbacks[0].event.item_key, "boss_box_data")
        self.assertEqual(correlator.collect_save_fallbacks(), [])

    def test_unmatched_log_is_not_emitted(self) -> None:
        correlator = ChestDropCorrelator(confirmation_window_seconds=0.05)

        correlator.register_log_drop(_boss_log_event(), stage_key=3205)
        time.sleep(0.06)

        self.assertEqual(correlator.collect_save_fallbacks(), [])


if __name__ == "__main__":
    unittest.main()
