from __future__ import annotations

import time
from collections.abc import Callable

from src.data.stage_catalog import boss_chest_level_for_key


MONITOR_STARTUP_GRACE_SECONDS = 30.0


def should_accept_flat_count_drop(
    *,
    chest_level: int,
    last_drop_at: float | None,
    cooldown_seconds: float,
    timer_is_counting: bool,
    now: float | None = None,
    monitor_started_at: float | None = None,
) -> bool:
    """Accept a repeated GetBoxCount line when cooldown elapsed and timer is idle."""
    if timer_is_counting:
        return False

    current_time = time.time() if now is None else now

    if last_drop_at is None:
        if monitor_started_at is None:
            return True
        return current_time - monitor_started_at >= MONITOR_STARTUP_GRACE_SECONDS

    return current_time - last_drop_at >= cooldown_seconds


class DropCooldownRegistry:
    def __init__(
        self,
        *,
        cooldown_minutes_provider: Callable[[], float],
        is_timer_counting: Callable[[int], bool] | None = None,
        last_drop_by_level: dict[int, float] | None = None,
        monitor_started_at: float | None = None,
    ) -> None:
        self._cooldown_minutes_provider = cooldown_minutes_provider
        self._is_timer_counting = is_timer_counting or (lambda _level: False)
        self._last_drop_by_level: dict[int, float] = dict(last_drop_by_level or {})
        self._monitor_started_at = (
            time.time() if monitor_started_at is None else monitor_started_at
        )

    def snapshot(self) -> dict[int, float]:
        return dict(self._last_drop_by_level)

    def record_drop(self, chest_level: int, *, at: float | None = None) -> None:
        self._last_drop_by_level[chest_level] = time.time() if at is None else at

    def last_drop_at(self, chest_level: int) -> float | None:
        return self._last_drop_by_level.get(chest_level)

    def should_accept_flat_count_for_key(self, item_key: str) -> bool:
        chest_level = boss_chest_level_for_key(item_key)
        if chest_level is None:
            return False
        return should_accept_flat_count_drop(
            chest_level=chest_level,
            last_drop_at=self._last_drop_by_level.get(chest_level),
            cooldown_seconds=self._cooldown_minutes_provider() * 60.0,
            timer_is_counting=self._is_timer_counting(chest_level),
            monitor_started_at=self._monitor_started_at,
        )
