from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from src.infrastructure.game_paths import (
    SAVE_FILE_NAME,
    SAVE_FILE_TEST_BACKUP_NAME,
    is_active_save_file_name,
    list_active_save_candidates,
)
from src.infrastructure.save_reader import BoxDataSnapshot, SaveSnapshot, pick_preferred_snapshot


class ActiveSaveFileNameTests(unittest.TestCase):
    def test_accepts_main_and_rotation_files(self) -> None:
        self.assertTrue(is_active_save_file_name(SAVE_FILE_NAME))
        self.assertTrue(is_active_save_file_name(SAVE_FILE_TEST_BACKUP_NAME))
        self.assertTrue(is_active_save_file_name("SaveFile_Live_3.es3.bak"))

    def test_rejects_dated_manual_backups(self) -> None:
        self.assertFalse(is_active_save_file_name("SaveFile_Live_backup_20260611_073315.es3"))


class ActiveSaveCandidateTests(unittest.TestCase):
    def test_lists_only_active_rotation_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            main = directory / SAVE_FILE_NAME
            rotation = directory / "SaveFile_Live_2.es3.bak"
            manual = directory / "SaveFile_Live_backup_20260611_073315.es3"
            main.write_text("main", encoding="utf-8")
            rotation.write_text("rotation", encoding="utf-8")
            manual.write_text("manual", encoding="utf-8")

            candidates = list_active_save_candidates(main)
            names = {path.name for path in candidates}

            self.assertEqual(names, {SAVE_FILE_NAME, "SaveFile_Live_2.es3.bak"})


class PickPreferredSnapshotTests(unittest.TestCase):
    def _snapshot(self, stage_key: int, boss: int, normal: int) -> SaveSnapshot:
        return SaveSnapshot(
            current_stage_key=stage_key,
            box_data=BoxDataSnapshot(
                box_types=(1, 0),
                box_quantities=(boss, normal),
            ),
        )

    def test_prefers_highest_box_counts_over_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            stale = directory / "SaveFile_Live.es3"
            fresh = directory / "SaveFile_Live_1.es3.bak"
            stale.write_text("stale", encoding="utf-8")
            fresh.write_text("fresh", encoding="utf-8")

            source, snapshot = pick_preferred_snapshot(
                [
                    (stale, self._snapshot(stage_key=3205, boss=2, normal=0)),
                    (fresh, self._snapshot(stage_key=3205, boss=3, normal=0)),
                ]
            )

            self.assertEqual(source.name, "SaveFile_Live_1.es3.bak")
            self.assertEqual(snapshot.boss_box_count, 3)

    def test_tie_breaks_by_latest_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            older = directory / "SaveFile_Live.es3"
            newer = directory / "SaveFile_Live_1.es3.bak"
            older.write_text("older", encoding="utf-8")
            newer.write_text("newer", encoding="utf-8")
            now = time.time()
            os.utime(older, (now - 10, now - 10))
            os.utime(newer, (now, now))

            source, snapshot = pick_preferred_snapshot(
                [
                    (older, self._snapshot(stage_key=1308, boss=2, normal=1)),
                    (newer, self._snapshot(stage_key=3205, boss=2, normal=1)),
                ]
            )

            self.assertEqual(source.name, "SaveFile_Live_1.es3.bak")
            self.assertEqual(snapshot.current_stage_key, 3205)


if __name__ == "__main__":
    unittest.main()
