from __future__ import annotations

import time
from dataclasses import dataclass

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_event_validator import is_chest_event_consistent_with_stage

CONFIRMATION_WINDOW_SECONDS = 15.0


@dataclass(frozen=True)
class ConfirmedChestDrop:
    event: ChestEvent
    stage_key: int


@dataclass
class _SaveDropSignal:
    event: ChestEvent
    stage_key: int
    detected_at: float


@dataclass
class _LogDropSignal:
    event: ChestEvent
    stage_key: int
    detected_at: float


class ChestDropCorrelator:
    """Correlates save BoxData increases with Player.log GetBoxCount lines."""

    def __init__(self, *, confirmation_window_seconds: float = CONFIRMATION_WINDOW_SECONDS) -> None:
        self._confirmation_window_seconds = confirmation_window_seconds
        self._pending_saves: list[_SaveDropSignal] = []
        self._pending_logs: list[_LogDropSignal] = []

    def register_save_drop(self, event: ChestEvent, stage_key: int) -> list[ConfirmedChestDrop]:
        now = time.time()
        self._prune_stale(now)
        signal = _SaveDropSignal(event=event, stage_key=stage_key, detected_at=now)
        confirmed = self._match_save_with_pending_logs(signal)
        if confirmed is None:
            self._pending_saves.append(signal)
            return []
        return [confirmed]

    def register_log_drop(self, event: ChestEvent, stage_key: int) -> list[ConfirmedChestDrop]:
        now = time.time()
        self._prune_stale(now)
        signal = _LogDropSignal(event=event, stage_key=stage_key, detected_at=now)
        confirmed = self._match_log_with_pending_saves(signal)
        if confirmed is None:
            self._pending_logs.append(signal)
            return []
        return [confirmed]

    def collect_save_fallbacks(self) -> list[ConfirmedChestDrop]:
        now = time.time()
        ready: list[ConfirmedChestDrop] = []
        still_pending: list[_SaveDropSignal] = []

        for signal in self._pending_saves:
            age = now - signal.detected_at
            if age < self._confirmation_window_seconds:
                still_pending.append(signal)
                continue
            ready.append(
                ConfirmedChestDrop(event=signal.event, stage_key=signal.stage_key)
            )

        self._pending_saves = still_pending
        return ready

    def _prune_stale(self, now: float) -> None:
        self._pending_logs = [
            signal
            for signal in self._pending_logs
            if now - signal.detected_at <= self._confirmation_window_seconds
        ]

    def _match_save_with_pending_logs(
        self,
        save_signal: _SaveDropSignal,
    ) -> ConfirmedChestDrop | None:
        for index, log_signal in enumerate(self._pending_logs):
            if not self._signals_match(save_signal, log_signal):
                continue
            self._pending_logs.pop(index)
            return ConfirmedChestDrop(
                event=log_signal.event,
                stage_key=save_signal.stage_key,
            )
        return None

    def _match_log_with_pending_saves(
        self,
        log_signal: _LogDropSignal,
    ) -> ConfirmedChestDrop | None:
        for index, save_signal in enumerate(self._pending_saves):
            if not self._signals_match(save_signal, log_signal):
                continue
            self._pending_saves.pop(index)
            return ConfirmedChestDrop(
                event=log_signal.event,
                stage_key=save_signal.stage_key,
            )
        return None

    def _signals_match(self, save_signal: _SaveDropSignal, log_signal: _LogDropSignal) -> bool:
        if save_signal.event.chest_type != log_signal.event.chest_type:
            return False

        if (
            abs(save_signal.detected_at - log_signal.detected_at)
            > self._confirmation_window_seconds
        ):
            return False

        if log_signal.event.chest_type == ChestType.NORMAL_BROWN:
            return True

        return is_chest_event_consistent_with_stage(log_signal.event, save_signal.stage_key)
