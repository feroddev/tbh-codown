from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config_loader import load_config, save_config
from src.infrastructure.game_paths import (
    DEFAULT_ES3_PASSWORD,
    Es3PasswordDiscovery,
    discover_es3_password,
    discover_es3_password_result,
)


class Es3PasswordDiscoveryTests(unittest.TestCase):
    def test_returns_default_when_resources_assets_is_missing(self) -> None:
        missing_path = Path("/tmp/tbh-monitor-missing-resources.assets")

        result = discover_es3_password_result(missing_path)

        self.assertEqual(
            result,
            Es3PasswordDiscovery(password=DEFAULT_ES3_PASSWORD, from_game=False),
        )
        self.assertEqual(discover_es3_password(missing_path), DEFAULT_ES3_PASSWORD)

    def test_extracts_password_from_resources_assets(self) -> None:
        marker = b"SaveFile_Live.es3\x00customPassword123\x00"
        payload = b"prefix" + marker + b"suffix"

        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(payload)
            resources_path = Path(handle.name)

        try:
            result = discover_es3_password_result(resources_path)
        finally:
            resources_path.unlink(missing_ok=True)

        self.assertEqual(
            result,
            Es3PasswordDiscovery(password="customPassword123", from_game=True),
        )


class LoadConfigEs3PasswordTests(unittest.TestCase):
    def test_marks_default_password_when_discovery_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            config_path.write_text("paths:\n  state_file: state.json\n", encoding="utf-8")

            with patch(
                "src.infrastructure.game_paths.discover_es3_password_result",
                return_value=Es3PasswordDiscovery(
                    password=DEFAULT_ES3_PASSWORD,
                    from_game=False,
                ),
            ):
                loaded = load_config(config_path)

            self.assertTrue(loaded.es3_password_is_default)
            self.assertEqual(loaded.es3_password, DEFAULT_ES3_PASSWORD)

    def test_explicit_password_is_not_marked_as_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            config_path.write_text(
                "paths:\n  state_file: state.json\n  es3_password: user-set\n",
                encoding="utf-8",
            )

            loaded = load_config(config_path)

            self.assertFalse(loaded.es3_password_is_default)
            self.assertTrue(loaded.es3_password_from_config)
            self.assertEqual(loaded.es3_password, "user-set")

    def test_save_config_omits_auto_discovered_es3_password(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            config_path.write_text("paths:\n  state_file: state.json\n", encoding="utf-8")

            with patch(
                "src.infrastructure.game_paths.discover_es3_password_result",
                return_value=Es3PasswordDiscovery(
                    password="game-key-from-discovery",
                    from_game=True,
                ),
            ):
                loaded = load_config(config_path)

            save_config(config_path, loaded)
            saved_raw = config_path.read_text(encoding="utf-8")

            self.assertNotIn("es3_password", saved_raw)
            self.assertFalse(loaded.es3_password_from_config)

    def test_save_config_keeps_explicit_es3_password(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.yaml"
            config_path.write_text(
                "paths:\n  state_file: state.json\n  es3_password: user-set\n",
                encoding="utf-8",
            )
            loaded = load_config(config_path)

            save_config(config_path, loaded)

            self.assertIn("es3_password: user-set", config_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
