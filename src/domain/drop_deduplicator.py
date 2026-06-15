from __future__ import annotations

import time


class DropDeduplicator:
    def __init__(self, window_seconds: float = 6.0) -> None:
        self._window_seconds = window_seconds
        self._recent: list[tuple[float, str]] = []

    def is_duplicate(self, dedup_key: str) -> bool:
        now = time.time()
        self._recent = [
            entry
            for entry in self._recent
            if now - entry[0] < self._window_seconds
        ]
        for _, recent_key in self._recent:
            if recent_key == dedup_key:
                return True
        self._recent.append((now, dedup_key))
        return False
