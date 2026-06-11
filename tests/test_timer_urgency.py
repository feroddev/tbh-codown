from __future__ import annotations

import time
import unittest

from src.domain.timer_urgency import (
    TimerSortState,
    pick_next_collectable_key,
    sort_timer_keys_by_urgency,
)


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

    def test_expired_jumps_above_higher_priority_active(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=40, priority=1, expires_at=now + 600, expired=False),
            TimerSortState(timer_key=30, priority=2, expires_at=None, expired=True),
        ]
        self.assertEqual(sort_timer_keys_by_urgency(states), [30, 40])

    def test_pick_next_collectable_skips_active_timers(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=40, priority=1, expires_at=now + 30, expired=False),
            TimerSortState(timer_key=30, priority=2, expires_at=None, expired=True),
        ]
        self.assertEqual(pick_next_collectable_key(states), 30)

    def test_pick_next_collectable_none_when_all_counting(self) -> None:
        now = time.time()
        states = [
            TimerSortState(timer_key=40, priority=1, expires_at=now + 30, expired=False),
            TimerSortState(timer_key=30, priority=2, expires_at=now + 120, expired=False),
        ]
        self.assertIsNone(pick_next_collectable_key(states))

    def test_pick_next_collectable_uses_priority_among_expired(self) -> None:
        states = [
            TimerSortState(timer_key=50, priority=3, expires_at=None, expired=True),
            TimerSortState(timer_key=40, priority=1, expires_at=None, expired=True),
        ]
        self.assertEqual(pick_next_collectable_key(states), 40)


if __name__ == "__main__":
    unittest.main()
