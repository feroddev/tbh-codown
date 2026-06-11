from __future__ import annotations

import time
import unittest

from src.domain.timer_urgency import TimerSortState, sort_timer_keys_by_urgency


class TimerUrgencyTests(unittest.TestCase):
    def test_expired_comes_before_active(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=40, priority=1, expires_at=now + 120, expired=False),
            TimerSortState(timer_key=30, priority=2, expires_at=None, expired=True),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [30, 40])

    def test_active_sorted_by_remaining_time(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=50, priority=1, expires_at=now + 300, expired=False),
            TimerSortState(timer_key=40, priority=2, expires_at=now + 60, expired=False),
            TimerSortState(timer_key=30, priority=3, expires_at=now + 180, expired=False),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [40, 30, 50])

    def test_waiting_comes_after_active_and_expired(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=20, priority=1, expires_at=None, expired=False),
            TimerSortState(timer_key=40, priority=2, expires_at=now + 30, expired=False),
            TimerSortState(timer_key=30, priority=3, expires_at=None, expired=True),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [30, 40, 20])

    def test_tiebreaker_uses_priority(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=50, priority=3, expires_at=None, expired=True),
            TimerSortState(timer_key=40, priority=1, expires_at=None, expired=True),
            TimerSortState(timer_key=30, priority=2, expires_at=None, expired=True),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [40, 30, 50])

    def test_waiting_sorted_by_priority(self) -> None:
        states = [
            TimerSortState(timer_key=50, priority=3, expires_at=None, expired=False),
            TimerSortState(timer_key=40, priority=1, expires_at=None, expired=False),
            TimerSortState(timer_key=30, priority=2, expires_at=None, expired=False),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [40, 30, 50])


if __name__ == "__main__":
    unittest.main()
