from __future__ import annotations

import re
import time
from collections.abc import Callable
from pathlib import Path

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_key_classifier import classify_chest_item_key

GET_BOX_COUNT_PATTERN = re.compile(
    r"GetBoxCount Success Count\s*:\s*(\d+)\s*//\s*ItemKey\s*:\s*(\d+)"
)
INVENTORY_BURST_MIN_KEYS = 3


def is_inventory_sync_burst(events: list[ChestEvent]) -> bool:
    if len(events) < INVENTORY_BURST_MIN_KEYS:
        return False
    unique_keys = {event.item_key for event in events}
    return len(unique_keys) >= INVENTORY_BURST_MIN_KEYS


class ChestDetector:
    def __init__(
        self,
        *,
        consider_common_chest: bool,
        on_chest_detected: Callable[[ChestEvent], None] | None = None,
        debounce_seconds: float = 4.0,
    ) -> None:
        self._consider_common_chest = consider_common_chest
        self._on_chest_detected = on_chest_detected
        self._debounce_seconds = debounce_seconds
        self._last_event_at_by_key: dict[str, float] = {}
        self._use_count_tracking = False
        self._last_counts: dict[str, int] = {}

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._consider_common_chest = enabled

    def enable_count_tracking(self, enabled: bool) -> None:
        self._use_count_tracking = enabled

    def process_line(self, line: str) -> ChestEvent | None:
        match = GET_BOX_COUNT_PATTERN.search(line)
        if not match:
            return None

        count = int(match.group(1))
        item_key = match.group(2)
        chest_type = classify_chest_item_key(
            item_key,
            consider_common_chest=self._consider_common_chest,
        )
        if chest_type is None:
            return None

        if self._use_count_tracking:
            previous_count = self._last_counts.get(item_key, 0)
            if count <= previous_count:
                return None
            self._last_counts[item_key] = max(previous_count, count)
        else:
            now = time.time()
            last_event_at = self._last_event_at_by_key.get(item_key)
            if last_event_at is not None and now - last_event_at < self._debounce_seconds:
                return None
            self._last_event_at_by_key[item_key] = now

        event = ChestEvent(
            item_key=item_key,
            chest_type=chest_type,
            count=count,
            raw_line=line.strip(),
        )
        if self._on_chest_detected is not None:
            self._on_chest_detected(event)
        return event


class PlayerLogPoller:
    def __init__(
        self,
        log_path: Path,
        *,
        consider_common_chest: bool,
        debounce_seconds: float = 4.0,
    ) -> None:
        self._log_path = log_path
        self._detector = ChestDetector(
            consider_common_chest=consider_common_chest,
            debounce_seconds=debounce_seconds,
        )
        self._file_handle = None
        self._inode: tuple[int, int] | None = None

    def _open_log_at_end(self) -> None:
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None

        if not self._log_path.exists():
            return

        self._file_handle = self._log_path.open("r", encoding="utf-8", errors="replace")
        stat = self._log_path.stat()
        self._inode = (stat.st_ino, stat.st_size)
        self._file_handle.seek(0, 2)

    def _maybe_reopen(self) -> None:
        if not self._log_path.exists():
            return

        stat = self._log_path.stat()
        current_inode = (stat.st_ino, stat.st_size)
        if self._inode is None or current_inode[0] != self._inode[0]:
            self._open_log_at_end()

    def poll(self) -> list[ChestEvent]:
        if self._file_handle is None:
            self._open_log_at_end()
        if self._file_handle is None:
            return []

        self._maybe_reopen()
        batch_events: list[ChestEvent] = []
        while True:
            line = self._file_handle.readline()
            if not line:
                break
            event = self._detector.process_line(line.rstrip("\n"))
            if event is not None:
                batch_events.append(event)

        if is_inventory_sync_burst(batch_events):
            return []
        return batch_events

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._detector.set_consider_common_chest(enabled)

    def close(self) -> None:
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None


class LogWatcher:
    def __init__(
        self,
        log_path: Path,
        detector: ChestDetector,
        chest_item_keys: dict[str, list[str]] | None = None,
        poll_interval_seconds: float = 0.5,
    ) -> None:
        self._log_path = log_path
        self._detector = detector
        self._poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._poller = PlayerLogPoller(
            log_path,
            consider_common_chest=True,
            debounce_seconds=detector._debounce_seconds,
        )

    def stop(self) -> None:
        self._running = False
        self._poller.close()

    def run(self) -> None:
        self._running = True
        while self._running:
            for event in self._poller.poll():
                if self._detector._on_chest_detected is not None:
                    self._detector._on_chest_detected(event)
            time.sleep(self._poll_interval_seconds)

    def replay_file(self, log_path: Path, *, consider_common_chest: bool = False) -> list[ChestEvent]:
        events: list[ChestEvent] = []
        replay_detector = ChestDetector(
            consider_common_chest=consider_common_chest,
            debounce_seconds=0.0,
        )
        replay_detector.enable_count_tracking(True)

        with log_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                event = replay_detector.process_line(line)
                if event is not None:
                    events.append(event)

        return events
