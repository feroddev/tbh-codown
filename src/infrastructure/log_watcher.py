from __future__ import annotations

import re
import time
from collections import Counter, deque
from collections.abc import Callable
from pathlib import Path

from src.domain.chest_event import ChestEvent, ChestType
from src.domain.chest_key_classifier import classify_chest_item_key

GET_BOX_COUNT_PATTERN = re.compile(
    r"GetBoxCount Success Count\s*:\s*(\d+)\s*//\s*ItemKey\s*:\s*(\d+)"
)
INVENTORY_BURST_MIN_KEYS = 3
LOG_SEED_TAIL_LINES = 400


def is_inventory_sync_burst(events: list[ChestEvent]) -> bool:
    """Detect Steam inventory recount bursts (one line per owned chest type).

    Real multi-drops repeat the same item key; inventory sync queries each key once.
    """
    if len(events) < INVENTORY_BURST_MIN_KEYS:
        return False
    key_counts = Counter(event.item_key for event in events)
    if len(key_counts) < INVENTORY_BURST_MIN_KEYS:
        return False
    return all(count == 1 for count in key_counts.values())


def filter_inventory_sync_burst(
    events: list[ChestEvent],
    *,
    preserve_item_keys: frozenset[str] = frozenset(),
) -> list[ChestEvent]:
    if not is_inventory_sync_burst(events):
        return events

    key_counts = Counter(event.item_key for event in events)
    return [
        event
        for event in events
        if event.count_increased
        or key_counts[event.item_key] > 1
        or event.item_key in preserve_item_keys
    ]


class ChestDetector:
    def __init__(
        self,
        *,
        consider_common_chest: bool,
        on_chest_detected: Callable[[ChestEvent], None] | None = None,
        debounce_seconds: float = 4.0,
        watch_boss_keys: frozenset[str] = frozenset(),
        watch_common_keys: frozenset[str] = frozenset(),
        flat_count_drop_gate: Callable[[str], bool] | None = None,
    ) -> None:
        self._consider_common_chest = consider_common_chest
        self._on_chest_detected = on_chest_detected
        self._debounce_seconds = debounce_seconds
        self._use_count_tracking = False
        self._last_counts: dict[str, int] = {}
        self._last_emitted_count: dict[str, int] = {}
        self._watch_boss_keys = watch_boss_keys
        self._watch_common_keys = watch_common_keys
        self._flat_count_drop_gate = flat_count_drop_gate

    def set_flat_count_drop_gate(
        self,
        gate: Callable[[str], bool] | None,
    ) -> None:
        self._flat_count_drop_gate = gate

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._consider_common_chest = enabled

    def set_watch_boss_keys(self, keys: frozenset[str]) -> None:
        self._watch_boss_keys = keys

    def set_watch_common_keys(self, keys: frozenset[str]) -> None:
        self._watch_common_keys = keys

    def enable_count_tracking(self, enabled: bool) -> None:
        self._use_count_tracking = enabled

    def seed_line(self, line: str) -> None:
        match = GET_BOX_COUNT_PATTERN.search(line)
        if not match:
            return

        count = int(match.group(1))
        item_key = match.group(2)
        chest_type = classify_chest_item_key(
            item_key,
            consider_common_chest=self._consider_common_chest,
        )
        if chest_type is None:
            return

        self._last_counts[item_key] = count

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

        count_increased = False

        if self._use_count_tracking:
            had_known_count = item_key in self._last_counts
            previous_count = self._last_counts.get(item_key)
            self._last_counts[item_key] = count

            if previous_count is None:
                if count > 0 and self._is_watched_item_key(item_key):
                    previous_count = 0
                else:
                    return None

            count_increased = had_known_count and count > previous_count

            if count <= previous_count:
                if not self._should_accept_flat_count_drop(item_key):
                    return None
                last_emitted = self._last_emitted_count.get(item_key)
                if last_emitted is not None and count <= last_emitted:
                    return None

        self._last_emitted_count[item_key] = count

        event = ChestEvent(
            item_key=item_key,
            chest_type=chest_type,
            count=count,
            raw_line=line.strip(),
            count_increased=count_increased,
        )
        if self._on_chest_detected is not None:
            self._on_chest_detected(event)
        return event

    def _is_watched_item_key(self, item_key: str) -> bool:
        if item_key in self._watch_boss_keys:
            return True
        return self._consider_common_chest and item_key in self._watch_common_keys

    def _should_accept_flat_count_drop(self, item_key: str) -> bool:
        if self._flat_count_drop_gate is None:
            return False
        if not self._is_watched_item_key(item_key):
            return False
        return self._flat_count_drop_gate(item_key)


class PlayerLogPoller:
    def __init__(
        self,
        log_path: Path,
        *,
        consider_common_chest: bool,
        debounce_seconds: float = 4.0,
        watch_boss_keys: frozenset[str] = frozenset(),
        watch_common_keys: frozenset[str] = frozenset(),
        flat_count_drop_gate: Callable[[str], bool] | None = None,
    ) -> None:
        self._log_path = log_path
        self._detector = ChestDetector(
            consider_common_chest=consider_common_chest,
            debounce_seconds=debounce_seconds,
            watch_boss_keys=watch_boss_keys,
            watch_common_keys=watch_common_keys,
            flat_count_drop_gate=flat_count_drop_gate,
        )
        self._detector.enable_count_tracking(True)
        self._file_handle = None
        self._inode: tuple[int, int] | None = None

    def set_consider_common_chest(self, enabled: bool) -> None:
        self._detector.set_consider_common_chest(enabled)

    def set_watch_boss_keys(self, keys: frozenset[str]) -> None:
        self._detector.set_watch_boss_keys(keys)

    def set_watch_common_keys(self, keys: frozenset[str]) -> None:
        self._detector.set_watch_common_keys(keys)

    def set_flat_count_drop_gate(
        self,
        gate: Callable[[str], bool] | None,
    ) -> None:
        self._detector.set_flat_count_drop_gate(gate)

    def seed_from_log_tail(self, *, max_lines: int = LOG_SEED_TAIL_LINES) -> None:
        if not self._log_path.exists():
            return

        tail: deque[str] = deque(maxlen=max_lines)
        with self._log_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                tail.append(line.rstrip("\n"))

        for line in tail:
            self._detector.seed_line(line)

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
        elif stat.st_size < self._inode[1]:
            self._open_log_at_end()
        self._inode = current_inode

    def poll(
        self,
        *,
        preserve_item_keys: frozenset[str] = frozenset(),
    ) -> list[ChestEvent]:
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

        return filter_inventory_sync_burst(
            batch_events,
            preserve_item_keys=preserve_item_keys,
        )

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
            watch_boss_keys=detector._watch_boss_keys,
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
