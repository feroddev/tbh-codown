from __future__ import annotations

import time
from collections.abc import Callable

from src.data.chest_catalog import common_chest_level_for_key
from src.data.stage_catalog import boss_chest_level_for_key
from src.domain.chest_key_classifier import is_common_chest_item_key, is_stage_boss_item_key
from src.domain.chest_timer_keys import common_chest_timer_key


MONITOR_STARTUP_GRACE_SECONDS = 30.0
COOLDOWN_TOLERANCE_SECONDS = 15.0


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

    return current_time - last_drop_at >= cooldown_seconds - COOLDOWN_TOLERANCE_SECONDS


class DropCooldownRegistry:
    def __init__(
        self,
        *,
        boss_cooldown_minutes_provider: Callable[[], float],
        common_cooldown_minutes_provider: Callable[[], float],
        is_boss_timer_counting: Callable[[int], bool] | None = None,
        is_common_timer_counting: Callable[[int], bool] | None = None,
        last_drop_by_level: dict[int, float] | None = None,
        monitor_started_at: float | None = None,
    ) -> None:
        self._boss_cooldown_minutes_provider = boss_cooldown_minutes_provider
        self._common_cooldown_minutes_provider = common_cooldown_minutes_provider
        self._is_boss_timer_counting = is_boss_timer_counting or (lambda _level: False)
        self._is_common_timer_counting = is_common_timer_counting or (lambda _level: False)
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
        if is_stage_boss_item_key(item_key):
            chest_level = boss_chest_level_for_key(item_key)
            if chest_level is None:
                return False
            return should_accept_flat_count_drop(
                chest_level=chest_level,
                last_drop_at=self._last_drop_by_level.get(chest_level),
                cooldown_seconds=self._boss_cooldown_minutes_provider() * 60.0,
                timer_is_counting=self._is_boss_timer_counting(chest_level),
                monitor_started_at=self._monitor_started_at,
            )

        if is_common_chest_item_key(item_key):
            chest_level = common_chest_level_for_key(item_key)
            if chest_level is None:
                return False
            timer_key = common_chest_timer_key(chest_level)
            return should_accept_flat_count_drop(
                chest_level=timer_key,
                last_drop_at=self._last_drop_by_level.get(timer_key),
                cooldown_seconds=self._common_cooldown_minutes_provider() * 60.0,
                timer_is_counting=self._is_common_timer_counting(chest_level),
                monitor_started_at=self._monitor_started_at,
            )

        return False
