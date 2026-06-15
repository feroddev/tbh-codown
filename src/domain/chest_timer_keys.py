from __future__ import annotations


def common_chest_timer_key(chest_level: int) -> int:
    return -abs(chest_level)


def chest_level_from_timer_key(timer_key: int) -> int:
    return abs(timer_key)


def is_common_chest_timer_key(timer_key: int) -> bool:
    return timer_key < 0


def is_boss_chest_timer_key(timer_key: int) -> bool:
    return timer_key > 0
