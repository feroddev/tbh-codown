from __future__ import annotations

import unittest

from src.data.chest_catalog import common_chest_level_for_key
from src.domain.chest_timer_keys import (
    chest_level_from_timer_key,
    common_chest_timer_key,
    is_common_chest_timer_key,
)


class ChestTimerKeyTests(unittest.TestCase):
    def test_common_chest_timer_key_is_negative_level(self) -> None:
        self.assertEqual(common_chest_timer_key(50), -50)
        self.assertEqual(chest_level_from_timer_key(-50), 50)
        self.assertTrue(is_common_chest_timer_key(-50))

    def test_common_chest_key_for_level_maps_50_to_910501(self) -> None:
        from src.data.chest_catalog import common_chest_key_for_level

        self.assertEqual(common_chest_key_for_level(50), "910501")

    def test_common_chest_level_for_key_maps_910501_to_50(self) -> None:
        self.assertEqual(common_chest_level_for_key("910501"), 50)


if __name__ == "__main__":
    unittest.main()
