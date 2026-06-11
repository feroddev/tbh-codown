from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimerSortState:
    timer_key: int
    priority: int
    expires_at: float | None
    expired: bool


def sort_timer_keys_by_urgency(states: list[TimerSortState]) -> list[int]:
    """Sort timers for display.

    Collectable chests (expired / 0:00) are pulled to the top by priority.
    Remaining active timers follow by soonest expiry; waiting timers keep priority.
    """
    if not states:
        return []

    expired = sorted(
        (state for state in states if state.expired),
        key=lambda state: state.priority,
    )
    active = sorted(
        (state for state in states if not state.expired and state.expires_at is not None),
        key=lambda state: (state.expires_at, state.priority),
    )
    waiting = sorted(
        (state for state in states if not state.expired and state.expires_at is None),
        key=lambda state: state.priority,
    )

    ordered = expired + active + waiting
    return [state.timer_key for state in ordered]


def pick_next_collectable_key(states: list[TimerSortState]) -> int | None:
    """Return the next chest map to visit — only timers at 0:00 qualify."""
    expired = sorted(
        (state for state in states if state.expired),
        key=lambda state: state.priority,
    )
    if not expired:
        return None
    return expired[0].timer_key
