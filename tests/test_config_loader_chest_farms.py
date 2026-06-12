import tempfile
import unittest
from pathlib import Path

from src.config_loader import load_config, save_config
from src.domain.chest_farm import ChestFarmSlot


class ConfigLoaderChestFarmTests(unittest.TestCase):
    def test_load_preserves_clear_time_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            save_config(
                config_path,
                load_config(Path(__file__).resolve().parents[1] / "config.yaml"),
            )
            raw = config_path.read_text(encoding="utf-8")
            raw = raw.replace(
                "priority: 3\n",
                "priority: 3\n  clear_time_seconds: 157\n",
                1,
            )
            config_path.write_text(raw, encoding="utf-8")

            loaded = load_config(config_path)
            slot_40 = next(item for item in loaded.chest_farms if item.chest_level == 40)
            self.assertEqual(slot_40.stage_key, 2109)
            self.assertEqual(slot_40.clear_time_seconds, 157)

    def test_save_round_trips_clear_time_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            base = load_config(Path(__file__).resolve().parents[1] / "config.yaml")
            farms = [
                ChestFarmSlot(
                    chest_level=65,
                    stage_key=3205,
                    enabled=True,
                    priority=1,
                    clear_time_seconds=120,
                ),
                ChestFarmSlot(
                    chest_level=50,
                    stage_key=2305,
                    enabled=True,
                    priority=2,
                    clear_time_seconds=None,
                ),
            ]
            from dataclasses import replace

            updated = replace(base, chest_farms=farms)
            save_config(config_path, updated)
            reloaded = load_config(config_path)

            by_level = {slot.chest_level: slot for slot in reloaded.chest_farms}
            self.assertEqual(by_level[65].clear_time_seconds, 120)
            self.assertIsNone(by_level[50].clear_time_seconds)


if __name__ == "__main__":
    unittest.main()
