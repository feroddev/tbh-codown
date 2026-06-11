from __future__ import annotations

import json
import logging
import shutil
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from es3_modifier.main import ES3

from src.infrastructure.game_paths import discover_es3_password

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StageWriteResult:
    previous_stage_key: int
    new_stage_key: int
    backup_path: Path


class SaveWriter:
    def __init__(self, save_path: Path, password: str | None = None) -> None:
        self._save_path = save_path
        self._password = password or discover_es3_password()

    def _read_bytes(self) -> bytes:
        try:
            return self._save_path.read_bytes()
        except PermissionError:
            temp_copy = self._save_path.with_suffix(".es3.monitor_copy")
            shutil.copy2(self._save_path, temp_copy)
            data = temp_copy.read_bytes()
            temp_copy.unlink(missing_ok=True)
            return data

    def read_stage_key(self) -> int:
        encrypted = self._read_bytes()
        root = ES3(encrypted, self._password).load()
        player = json.loads(root["PlayerSaveData"]["value"])
        return int(player["commonSaveData"]["currentStageKey"])

    def write_stage_key(self, stage_key: int, reset_wave: bool = True) -> StageWriteResult:
        encrypted = self._read_bytes()
        es3 = ES3(encrypted, self._password)
        root = es3.load()
        player = json.loads(root["PlayerSaveData"]["value"])
        common = player["commonSaveData"]
        previous_stage_key = int(common["currentStageKey"])

        if previous_stage_key == stage_key and (not reset_wave or int(common.get("currentStageWave", 0)) == 0):
            backup_path = self._create_backup(encrypted)
            return StageWriteResult(previous_stage_key, stage_key, backup_path)

        common["currentStageKey"] = stage_key
        if reset_wave:
            common["currentStageWave"] = 0

        root["PlayerSaveData"]["value"] = json.dumps(player, separators=(",", ":"))
        updated = es3.save(json.dumps(root, separators=(",", ":")))
        backup_path = self._create_backup(encrypted)
        self._save_path.write_bytes(updated)
        logger.info("Save atualizado: stageKey %s -> %s", previous_stage_key, stage_key)
        return StageWriteResult(previous_stage_key, stage_key, backup_path)

    def _create_backup(self, encrypted: bytes) -> Path:
        backup_dir = self._save_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{self._save_path.stem}_{timestamp}.es3"
        backup_path.write_bytes(encrypted)
        return backup_path

    def wait_for_stage_key(
        self,
        stage_key: int,
        timeout_seconds: float = 45.0,
        poll_interval_seconds: float = 1.0,
    ) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            try:
                if self.read_stage_key() == stage_key:
                    return True
            except Exception as error:
                logger.debug("Aguardando save ficar legível: %s", error)
            time.sleep(poll_interval_seconds)
        return False
