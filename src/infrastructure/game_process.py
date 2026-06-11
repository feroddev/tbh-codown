from __future__ import annotations

import logging
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_GAME_EXE = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\TaskbarHero\TaskBarHero.exe"
)
DEFAULT_PROCESS_NAME = "TaskBarHero"


class GameProcessManager:
    def __init__(
        self,
        game_exe: Path,
        process_name: str = DEFAULT_PROCESS_NAME,
        startup_timeout_seconds: float = 45.0,
        shutdown_timeout_seconds: float = 15.0,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self._game_exe = game_exe
        self._process_name = process_name
        self._startup_timeout_seconds = startup_timeout_seconds
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._on_log = on_log

    def _log(self, message: str) -> None:
        logger.info(message)
        if self._on_log is not None:
            self._on_log(message)

    def is_running(self) -> bool:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {self._process_name}.exe", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.lower()
        return self._process_name.lower() in output and "no tasks are running" not in output

    def stop(self) -> None:
        if not self.is_running():
            self._log("Jogo já estava fechado")
            return

        self._log(f"Encerrando {self._process_name}")
        subprocess.run(
            ["taskkill", "/IM", f"{self._process_name}.exe", "/T"],
            capture_output=True,
            text=True,
            check=False,
        )

        deadline = time.time() + self._shutdown_timeout_seconds
        while time.time() < deadline:
            if not self.is_running():
                self._log("Jogo encerrado")
                return
            time.sleep(0.5)

        subprocess.run(
            ["taskkill", "/IM", f"{self._process_name}.exe", "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        self._log("Jogo encerrado (forçado)")

    def start(self) -> None:
        if not self._game_exe.exists():
            raise FileNotFoundError(f"Executável do jogo não encontrado: {self._game_exe}")

        if self.is_running():
            self._log("Jogo já está em execução")
            return

        self._log(f"Iniciando jogo: {self._game_exe.name}")
        subprocess.Popen(
            [str(self._game_exe)],
            cwd=str(self._game_exe.parent),
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )

        deadline = time.time() + self._startup_timeout_seconds
        while time.time() < deadline:
            if self.is_running():
                self._log("Jogo iniciado com sucesso")
                return
            time.sleep(1.0)

        raise TimeoutError("O jogo não iniciou dentro do tempo esperado")

    def restart(self) -> None:
        self.stop()
        time.sleep(1.0)
        self.start()
