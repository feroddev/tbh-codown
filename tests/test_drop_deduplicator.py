from __future__ import annotations

import unittest

from src.domain.drop_deduplicator import DropDeduplicator


class DropDeduplicatorTests(unittest.TestCase):
    def test_duplicate_key_is_rejected_within_window(self) -> None:
        deduplicator = DropDeduplicator(window_seconds=6.0)

        self.assertFalse(deduplicator.is_duplicate("normal_brown:2201:50"))
        self.assertTrue(deduplicator.is_duplicate("normal_brown:2201:50"))

    def test_different_keys_are_not_rejected(self) -> None:
        deduplicator = DropDeduplicator(window_seconds=6.0)

        self.assertFalse(deduplicator.is_duplicate("normal_brown:2201:50"))
        self.assertFalse(deduplicator.is_duplicate("boss:2201:50"))


if __name__ == "__main__":
    unittest.main()
