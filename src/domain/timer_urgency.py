from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimerSortState:
    timer_key: int
    priority: int
    expires_at: float | None
    expired: bool


def sort_timer_keys_by_urgency(states: list[TimerSortState]) -> list[int]:
    """Sort timers: expired first, then active by remaining time, then waiting.

    Within each urgency tier, lower ``priority`` values come first (rotation order).
    """
    if not states:
        return []

    def sort_key(state: TimerSortState) -> tuple:
        if state.expired:
            return (0, state.priority)
        if state.expires_at is not None:
            return (1, state.expires_at, state.priority)
        return (2, state.priority)

    return [state.timer_key for state in sorted(states, key=sort_key)]
