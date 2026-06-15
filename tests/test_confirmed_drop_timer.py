from __future__ import annotations

import unittest

import customtkinter as ctk

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_farm import ChestFarmSlot
from src.domain.chest_timer_keys import common_chest_timer_key
from src.domain.confirmed_drop_notification import ConfirmedDropNotification
from src.ui.chest_timer import ChestTimerBoard


class ConfirmedDropTimerIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._root = ctk.CTk()
        cls._root.withdraw()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._root.destroy()

    def test_first_confirmed_drop_starts_timer_for_watched_level(self) -> None:
        board = ChestTimerBoard(self._root, boss_duration_minutes=7.0)
        board.set_watch_targets(
            [
                ChestFarmSlot(
                    chest_level=65,
                    stage_key=3205,
                    enabled=True,
                    priority=1,
                    clear_time_seconds=146,
                )
            ]
        )

        event = ChestEvent("920651", ChestType.BOSS, 2, "")
        notification = ConfirmedDropNotification(
            event=event,
            stage_key=3205,
            chest_level=65,
            log_message="12:00:00 · Boss Chest Lv65",
        )

        watched = {65}
        self.assertIn(notification.chest_level, watched)
        self.assertTrue(board.has_timer_row(notification.chest_level))
        self.assertFalse(board.is_timer_counting(notification.chest_level))

        started = board.start_timer(notification.chest_level)

        self.assertTrue(started)
        self.assertTrue(board.is_timer_counting(notification.chest_level))

    def test_first_confirmed_common_drop_starts_common_timer_for_watched_level(
        self,
    ) -> None:
        board = ChestTimerBoard(
            self._root,
            boss_duration_minutes=7.0,
            common_duration_minutes=5.0,
            show_common_timer=True,
        )
        board.set_watch_targets(
            [
                ChestFarmSlot(
                    chest_level=50,
                    stage_key=2305,
                    enabled=True,
                    priority=1,
                    clear_time_seconds=120,
                )
            ]
        )

        event = ChestEvent("910501", ChestType.NORMAL_BROWN, 1, "")
        notification = ConfirmedDropNotification(
            event=event,
            stage_key=2305,
            chest_level=50,
            log_message="17:00:00 · Common Chest Lv50",
        )

        common_key = common_chest_timer_key(notification.chest_level)
        self.assertTrue(board.has_timer_row(common_key))
        self.assertFalse(board.is_timer_counting(common_key))

        started = board.start_timer(common_key)

        self.assertTrue(started)
        self.assertTrue(board.is_timer_counting(common_key))


if __name__ == "__main__":
    unittest.main()
