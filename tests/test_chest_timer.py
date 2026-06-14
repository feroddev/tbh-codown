from __future__ import annotations

import time
import unittest

from src.ui.chest_timer import ChestTimerRow


class ChestTimerRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import customtkinter as ctk

        cls._root = ctk.CTk()
        cls._root.withdraw()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._root.destroy()

    def _make_row(self) -> ChestTimerRow:
        return ChestTimerRow(
            self._root,
            timer_key=50,
            duration_minutes=12.0,
        )

    def test_is_counting_false_when_waiting(self) -> None:
        row = self._make_row()
        self.assertFalse(row.is_counting)

    def test_is_counting_true_while_active(self) -> None:
        row = self._make_row()
        row.start_countdown()
        self.assertTrue(row.is_counting)

    def test_is_counting_false_when_display_expired_but_deadline_remains(self) -> None:
        row = self._make_row()
        row.set_clear_time_seconds(30)
        row._expires_at = time.time() + 10
        row._expired = True
        self.assertFalse(row.is_counting)

    def test_start_countdown_on_drop_restarts_after_display_expired(self) -> None:
        row = self._make_row()
        row._expires_at = time.time() + 10
        row._expired = True

        started = row.start_countdown_on_drop()

        self.assertTrue(started)
        self.assertTrue(row.is_counting)
        self.assertFalse(row.is_expired)


if __name__ == "__main__":
    unittest.main()
