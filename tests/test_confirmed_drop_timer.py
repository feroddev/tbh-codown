from __future__ import annotations

import unittest

import customtkinter as ctk

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_farm import ChestFarmSlot
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
        board = ChestTimerBoard(self._root, duration_minutes=13.0)
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


if __name__ == "__main__":
    unittest.main()
