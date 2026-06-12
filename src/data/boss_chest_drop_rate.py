from __future__ import annotations


def format_boss_drop_percent(percent: float) -> str:
    if percent == int(percent):
        return f"{int(percent)}%"
    return f"{percent:g}%"


def effective_drop_percent(base_percent: float, rune_bonus_percent: float = 0) -> float:
    """Estimate boss chest drop % after rune multiplier (Taskbar Hero 1/1000 scale)."""
    base_per_mille = round(base_percent * 10)
    multiplier_per_mille = 1000 + int(rune_bonus_percent * 10)
    effective_per_mille = min(
        1000,
        (base_per_mille * multiplier_per_mille) // 1000,
    )
    return effective_per_mille / 10
