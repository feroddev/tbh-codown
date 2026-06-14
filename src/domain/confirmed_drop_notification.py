from __future__ import annotations

from dataclasses import dataclass

from src.domain.chest_event import ChestEvent


@dataclass(frozen=True)
class ConfirmedDropNotification:
    event: ChestEvent
    stage_key: int
    chest_level: int
    log_message: str
