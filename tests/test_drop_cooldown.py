from __future__ import annotations

import time
import unittest

from src.domain.drop_cooldown import DropCooldownRegistry, should_accept_flat_count_drop


class DropCooldownTests(unittest.TestCase):
    def test_should_accept_flat_count_drop_when_cooldown_elapsed(self) -> None:
        self.assertTrue(
            should_accept_flat_count_drop(
                chest_level=50,
                last_drop_at=1000.0,
                cooldown_seconds=13 * 60,
                timer_is_counting=False,
                now=1000.0 + 13 * 60,
            )
        )

    def test_should_reject_flat_count_drop_within_cooldown(self) -> None:
        self.assertFalse(
            should_accept_flat_count_drop(
                chest_level=50,
                last_drop_at=1000.0,
                cooldown_seconds=13 * 60,
                timer_is_counting=False,
                now=1000.0 + 12 * 60,
            )
        )

    def test_should_reject_flat_count_drop_when_timer_is_counting(self) -> None:
        self.assertFalse(
            should_accept_flat_count_drop(
                chest_level=50,
                last_drop_at=1000.0,
                cooldown_seconds=13 * 60,
                timer_is_counting=True,
                now=1000.0 + 20 * 60,
            )
        )

    def test_should_reject_flat_count_drop_without_previous_drop(self) -> None:
        self.assertFalse(
            should_accept_flat_count_drop(
                chest_level=50,
                last_drop_at=None,
                cooldown_seconds=13 * 60,
                timer_is_counting=False,
                now=5000.0,
            )
        )

    def test_registry_accepts_flat_count_for_boss_key_after_cooldown(self) -> None:
        registry = DropCooldownRegistry(
            cooldown_minutes_provider=lambda: 13.0,
            is_timer_counting=lambda _level: False,
            last_drop_by_level={50: 1000.0},
        )

        self.assertTrue(registry.should_accept_flat_count_for_key("920501"))

    def test_registry_rejects_flat_count_for_boss_key_within_cooldown(self) -> None:
        registry = DropCooldownRegistry(
            cooldown_minutes_provider=lambda: 13.0,
            is_timer_counting=lambda _level: False,
            last_drop_by_level={50: time.time()},
        )

        self.assertFalse(registry.should_accept_flat_count_for_key("920501"))


if __name__ == "__main__":
    unittest.main()
