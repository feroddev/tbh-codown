from __future__ import annotations

import logging
import time
from collections.abc import Callable

import pyautogui

from src.data.stage_codec import Difficulty, decode_stage_key
from src.domain.rotation_engine import MapConfig
from src.infrastructure.window_focus import focus_game_window

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.12

DIFFICULTY_TAB_KEYS = {
    Difficulty.NORMAL: "tab_normal",
    Difficulty.NIGHTMARE: "tab_nightmare",
    Difficulty.HELL: "tab_hell",
    Difficulty.TORMENT: "tab_torment",
}


class StageSwitcher:
    def __init__(
        self,
        window_title: str = "TaskBarHero",
        dry_run: bool = False,
        retry_attempts: int = 5,
        retry_delay_seconds: float = 1.0,
        global_ui: dict | None = None,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self._window_title = window_title
        self._dry_run = dry_run
        self._retry_attempts = retry_attempts
        self._retry_delay_seconds = retry_delay_seconds
        self._global_ui = global_ui or {}
        self._on_log = on_log

    def _log(self, message: str) -> None:
        logger.info(message)
        if self._on_log is not None:
            self._on_log(message)

    def _focus_window(self) -> tuple[int, int, int, int]:
        if self._dry_run:
            self._log(f"[simulação] Focaria a janela: {self._window_title}")
            return (0, 0, 800, 600)

        last_error: Exception | None = None
        for attempt in range(1, self._retry_attempts + 1):
            try:
                return focus_game_window(self._window_title)
            except Exception as error:
                last_error = error
                self._log(
                    f"Falha ao focar janela (tentativa {attempt}/{self._retry_attempts}): {error}"
                )
                time.sleep(self._retry_delay_seconds)

        raise RuntimeError(
            f"Não foi possível focar a janela do jogo: {self._window_title}"
        ) from last_error

    def _resolve_point(
        self,
        origin: tuple[int, int, int, int],
        point: dict[str, int | float] | None,
    ) -> tuple[int, int] | None:
        if not point:
            return None

        left, top, width, height = origin
        if "x_pct" in point and "y_pct" in point:
            return (
                int(left + float(point["x_pct"]) * width),
                int(top + float(point["y_pct"]) * height),
            )

        if "x" in point and "y" in point:
            return (int(left + int(point["x"])), int(top + int(point["y"])))

        return None

    def _click_point(self, origin: tuple[int, int, int, int], point: dict[str, int | float], label: str) -> None:
        resolved = self._resolve_point(origin, point)
        if resolved is None:
            raise ValueError(f"Coordenada inválida para: {label}")

        absolute_x, absolute_y = resolved
        if self._dry_run:
            self._log(f"[simulação] Clicaria em '{label}' em ({absolute_x}, {absolute_y})")
            return

        pyautogui.click(absolute_x, absolute_y)
        self._log(f"Clique em '{label}' ({absolute_x}, {absolute_y})")

    def _click_optional(self, origin, key: str, fallback_key: str | None, label: str) -> None:
        point = self._global_ui.get(key) or (self._global_ui.get(fallback_key) if fallback_key else None)
        if point:
            self._click_point(origin, point, label)
            time.sleep(0.35)
        else:
            self._log(f"Coordenada '{key}' não calibrada — etapa '{label}' ignorada")

    def switch_to_map(self, map_config: MapConfig) -> None:
        stage = decode_stage_key(map_config.stage_key)
        self._log(
            f"Trocando para {map_config.label} "
            f"(stageKey={map_config.stage_key}, {stage.difficulty.value} {stage.act}-{stage.stage})"
        )

        origin = self._focus_window()
        map_ui = map_config.ui

        self._click_optional(origin, "open_stage_menu", None, "abrir menu de stages")

        difficulty_tab = DIFFICULTY_TAB_KEYS[stage.difficulty]
        self._click_optional(origin, difficulty_tab, "open_difficulty_menu", f"aba {stage.difficulty.value}")

        act_key = f"act_{stage.act}"
        self._click_optional(origin, act_key, None, f"aba act {stage.act}")

        stage_point = map_ui.get("select_stage") or self._global_ui.get("stage_grid_origin")
        if stage_point is None:
            raise ValueError(
                f"Coordenadas 'select_stage' ausentes para o mapa {map_config.label}. "
                f"Calibre com: python -m src.main calibrate --map {map_config.priority}"
            )
        self._click_point(origin, stage_point, f"stage {stage.act}-{stage.stage}")
        time.sleep(0.2)

        confirm_point = map_ui.get("confirm") or self._global_ui.get("confirm_stage")
        if confirm_point:
            self._click_point(origin, confirm_point, "confirmar stage")
        else:
            self._log("Coordenada 'confirm_stage' não calibrada — confirmação ignorada")

        self._log(f"Troca de mapa concluída: {map_config.label}")
