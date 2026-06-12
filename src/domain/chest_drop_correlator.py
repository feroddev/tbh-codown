from __future__ import annotations

import time
from dataclasses import dataclass

from src.domain.chest_event import ChestEvent, ChestType

LOG_SAVE_SUPPRESS_SECONDS = 12.0


@dataclass(frozen=True)
class ConfirmedChestDrop:
    event: ChestEvent
    stage_key: int


@dataclass
class _RecentLogConfirm:
    chest_type: ChestType
    stage_key: int
    detected_at: float


class ChestDropCorrelator:
    """Confirms chest drops from Player.log immediately; save is optional backup."""

    def __init__(self, *, log_save_suppress_seconds: float = LOG_SAVE_SUPPRESS_SECONDS) -> None:
        self._log_save_suppress_seconds = log_save_suppress_seconds
        self._recent_log_confirms: list[_RecentLogConfirm] = []

    def register_save_drop(self, event: ChestEvent, stage_key: int) -> list[ConfirmedChestDrop]:
        now = time.time()
        self._prune_stale(now)

        if self._was_recently_confirmed_by_log(event.chest_type, stage_key, now):
            return []

        return [ConfirmedChestDrop(event=event, stage_key=stage_key)]

    def register_log_drop(self, event: ChestEvent, stage_key: int) -> list[ConfirmedChestDrop]:
        now = time.time()
        self._prune_stale(now)
        confirmed = ConfirmedChestDrop(event=event, stage_key=stage_key)
        self._record_log_confirm(confirmed, now)
        return [confirmed]

    def collect_save_fallbacks(self) -> list[ConfirmedChestDrop]:
        return []

    def _record_log_confirm(self, confirmed: ConfirmedChestDrop, now: float) -> None:
        self._recent_log_confirms.append(
            _RecentLogConfirm(
                chest_type=confirmed.event.chest_type,
                stage_key=confirmed.stage_key,
                detected_at=now,
            )
        )

    def _was_recently_confirmed_by_log(
        self,
        chest_type: ChestType,
        stage_key: int,
        now: float,
    ) -> bool:
        for recent in self._recent_log_confirms:
            if recent.chest_type != chest_type:
                continue
            if now - recent.detected_at > self._log_save_suppress_seconds:
                continue
            if recent.stage_key == stage_key:
                return True
        return False

    def _prune_stale(self, now: float) -> None:
        self._recent_log_confirms = [
            signal
            for signal in self._recent_log_confirms
            if now - signal.detected_at <= self._log_save_suppress_seconds
        ]
