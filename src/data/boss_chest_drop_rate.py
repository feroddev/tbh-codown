from __future__ import annotations


def format_boss_drop_percent(percent: float) -> str:
    if percent == int(percent):
        return f"{int(percent)}%"
    return f"{percent:g}%"
