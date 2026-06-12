import unittest

from src.domain.timer_urgency import (
    TimerSortState,
    pick_next_collectable_key,
    sort_timer_keys_by_urgency,
)


class TimerUrgencyTests(unittest.TestCase):
    NOW = 1_000_000.0

    def _state(
        self,
        level: int,
        priority: int,
        *,
        expires_at: float | None = None,
        expired: bool = False,
        clear_time_seconds: int = 0,
    ) -> TimerSortState:
        return TimerSortState(
            timer_key=level,
            priority=priority,
            expires_at=expires_at,
            expired=expired,
            clear_time_seconds=clear_time_seconds,
        )

    def test_case_1_rotation_ready_then_waiting_then_active(self) -> None:
        states = [
            self._state(65, 1, expired=True),
            self._state(40, 3),
            self._state(50, 2, expires_at=self.NOW + 290),
        ]
        self.assertEqual(
            sort_timer_keys_by_urgency(states, now=self.NOW),
            [65, 40, 50],
        )
        self.assertEqual(pick_next_collectable_key(states, now=self.NOW), 65)

    def test_case_2_waiting_before_active_by_display_time(self) -> None:
        states = [
            self._state(50, 2),
            self._state(65, 1, expires_at=self.NOW + 290),
            self._state(40, 3, expires_at=self.NOW + 720),
        ]
        self.assertEqual(
            sort_timer_keys_by_urgency(states, now=self.NOW),
            [50, 65, 40],
        )
        self.assertIsNone(pick_next_collectable_key(states, now=self.NOW))

    def test_case_3_rotation_ready_respects_priority_among_ready(self) -> None:
        states = [
            self._state(50, 2, expires_at=self.NOW + 30, clear_time_seconds=30),
            self._state(40, 3),
            self._state(65, 1, expires_at=self.NOW + 180),
        ]
        self.assertEqual(
            sort_timer_keys_by_urgency(states, now=self.NOW),
            [50, 40, 65],
        )
        self.assertEqual(pick_next_collectable_key(states, now=self.NOW), 50)

    def test_all_waiting_keeps_configured_priority(self) -> None:
        states = [
            self._state(65, 1),
            self._state(50, 2),
            self._state(40, 3),
        ]
        self.assertEqual(
            sort_timer_keys_by_urgency(states, now=self.NOW),
            [65, 50, 40],
        )


if __name__ == "__main__":
    unittest.main()
