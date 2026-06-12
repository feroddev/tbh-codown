from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class TimerSortState:
    timer_key: int
    priority: int
    expires_at: float | None
    expired: bool
    clear_time_seconds: int = 0


def display_remaining_seconds(
    state: TimerSortState,
    *,
    now: float | None = None,
) -> float | None:
    current_time = time.time() if now is None else now
    if state.expired:
        return 0.0
    if state.expires_at is None:
        return None
    return max(0.0, (state.expires_at - current_time) - state.clear_time_seconds)


def is_rotation_ready(
    state: TimerSortState,
    *,
    now: float | None = None,
) -> bool:
    if state.expired:
        return True
    remaining = display_remaining_seconds(state, now=now)
    if remaining is None:
        return False
    return remaining <= 0


def is_waiting(state: TimerSortState) -> bool:
    return not state.expired and state.expires_at is None


def is_active_counting(
    state: TimerSortState,
    *,
    now: float | None = None,
) -> bool:
    if state.expired or state.expires_at is None:
        return False
    remaining = display_remaining_seconds(state, now=now)
    return remaining is not None and remaining > 0


def sort_timer_keys_by_urgency(
    states: list[TimerSortState],
    *,
    now: float | None = None,
) -> list[int]:
    """Sort timers for display.

    1. Rotation ready (display 0:00) — by configured priority.
    2. Waiting (--:--) — by configured priority.
    3. Active countdown — by soonest display time, then priority.
    """
    if not states:
        return []

    current_time = time.time() if now is None else now

    rotation_ready = sorted(
        (state for state in states if is_rotation_ready(state, now=current_time)),
        key=lambda state: state.priority,
    )
    waiting = sorted(
        (state for state in states if is_waiting(state)),
        key=lambda state: state.priority,
    )
    active = sorted(
        (state for state in states if is_active_counting(state, now=current_time)),
        key=lambda state: (
            display_remaining_seconds(state, now=current_time) or 0.0,
            state.priority,
        ),
    )

    ordered = rotation_ready + waiting + active
    return [state.timer_key for state in ordered]


def pick_next_collectable_key(
    states: list[TimerSortState],
    *,
    now: float | None = None,
) -> int | None:
    """Return the next chest to visit — rotation display at 0:00, by priority."""
    current_time = time.time() if now is None else now
    ready = sorted(
        (state for state in states if is_rotation_ready(state, now=current_time)),
        key=lambda state: state.priority,
    )
    if not ready:
        return None
    return ready[0].timer_key
