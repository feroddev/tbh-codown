from __future__ import annotations

import logging
from collections.abc import Callable
from enum import Enum
from pathlib import Path

from src.data.stage_codec import decode_stage_key
from src.domain.rotation_engine import MapConfig
from src.infrastructure.game_paths import DEFAULT_GAME_EXE
from src.infrastructure.game_process import GameProcessManager
from src.infrastructure.save_writer import SaveWriter
from src.infrastructure.stage_switcher import StageSwitcher

logger = logging.getLogger(__name__)


class SwitchMethod(str, Enum):
    SAVE_RESTART = "save_restart"
    UI = "ui"


class MapSwitcher:
    def __init__(
        self,
        *,
        method: SwitchMethod,
        dry_run: bool,
        save_path: Path,
        es3_password: str,
        game_exe: Path = DEFAULT_GAME_EXE,
        window_title: str = "TaskBarHero",
        global_ui: dict | None = None,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self._method = method
        self._dry_run = dry_run
        self._save_writer = SaveWriter(save_path, password=es3_password)
        self._game_process = GameProcessManager(game_exe=game_exe, on_log=on_log)
        self._ui_switcher = StageSwitcher(
            window_title=window_title,
            dry_run=dry_run,
            global_ui=global_ui,
            on_log=on_log,
        )
        self._on_log = on_log

    def _log(self, message: str) -> None:
        logger.info(message)
        if self._on_log is not None:
            self._on_log(message)

    def switch_to_map(self, map_config: MapConfig) -> None:
        stage = decode_stage_key(map_config.stage_key)
        self._log(
            f"Trocando para {map_config.label} "
            f"(stageKey={map_config.stage_key}, {stage.difficulty.value} {stage.act}-{stage.stage})"
        )

        if self._method == SwitchMethod.SAVE_RESTART:
            self._switch_via_save_restart(map_config)
            return

        self._ui_switcher.switch_to_map(map_config)

    def _switch_via_save_restart(self, map_config: MapConfig) -> None:
        if self._dry_run:
            self._log(
                f"[simulação] Atualizaria save para stageKey={map_config.stage_key} "
                f"e reiniciaria o jogo"
            )
            return

        write_result = self._save_writer.write_stage_key(map_config.stage_key)
        self._log(
            f"Save alterado: {write_result.previous_stage_key} → {write_result.new_stage_key} "
            f"(backup em {write_result.backup_path.name})"
        )

        self._game_process.restart()

        if self._save_writer.wait_for_stage_key(map_config.stage_key):
            self._log(f"Jogo carregou o stageKey {map_config.stage_key}")
        else:
            self._log(
                f"Aviso: não foi possível confirmar stageKey {map_config.stage_key} após reinício"
            )

        self._log(f"Troca de mapa concluída: {map_config.label}")
