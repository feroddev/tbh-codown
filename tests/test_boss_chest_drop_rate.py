import unittest

from src.data.boss_chest_drop_rate import effective_drop_percent


class EffectiveDropPercentTests(unittest.TestCase):
    def test_no_rune_bonus_keeps_base_rate(self) -> None:
        self.assertEqual(effective_drop_percent(20.0, 0), 20.0)

    def test_additive_multiplier_from_rune_stat(self) -> None:
        self.assertEqual(effective_drop_percent(15.0, 300), 60.0)

    def test_pet_scale_bonus(self) -> None:
        self.assertEqual(effective_drop_percent(20.0, 15), 23.0)

    def test_high_bonus_is_capped_at_one_hundred_percent(self) -> None:
        self.assertEqual(effective_drop_percent(20.0, 490), 100.0)

    def test_uses_integer_per_mille_math(self) -> None:
        self.assertEqual(effective_drop_percent(15.3, 300), 61.2)


if __name__ == "__main__":
    unittest.main()
