from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk

from src.data.chest_catalog import chest_display_label
from src.domain.chest_farm import ChestFarmSlot
from src.ui.i18n import Language, format_watch_map_label_for_stage_key, t
from src.ui.sound_notifier import play_chest_drop_sound, play_timer_expired_sound
from src.ui.theme import (
    BG_ELEVATED,
    BG_INSET,
    BG_SURFACE,
    BORDER,
    BORDER_SUBTLE,
    DANGER,
    PAD_INNER,
    PAD_TIGHT,
    RADIUS_CARD,
    RADIUS_PANEL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TIMER_ACTIVE,
    TIMER_WAITING,
    hint_label,
    section_label,
)

TimerKey = int
EXPIRED_DISPLAY = "0:00"
WAITING_DISPLAY = "--:--"
ROW_HEIGHT = 34


@dataclass(frozen=True)
class TimerWatchTarget:
    chest_level: int
    stage_key: int
    priority: int


def _format_countdown(total_seconds: int) -> str:
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


class ChestTimerRow(ctk.CTkFrame):
    def __init__(
        self,
        master,
        timer_key: TimerKey,
        duration_minutes: float,
        *,
        map_label: str | None = None,
        language: Language = Language.PT_BR,
        on_drag_start: Callable[["ChestTimerRow"], None] | None = None,
        on_drag_motion: Callable[["ChestTimerRow", object], None] | None = None,
        on_drag_end: Callable[["ChestTimerRow"], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=BG_INSET,
            corner_radius=RADIUS_CARD,
            height=ROW_HEIGHT,
            border_width=1,
            border_color=BORDER,
            **kwargs,
        )
        self.pack_propagate(False)
        self._timer_key = timer_key
        self._map_label = map_label
        self._duration_seconds = max(1.0, duration_minutes * 60.0)
        self._expires_at: float | None = None
        self._expired = False
        self._language = language
        self._on_drag_start = on_drag_start
        self._on_drag_motion = on_drag_motion
        self._on_drag_end = on_drag_end

        self.grid_columnconfigure(3, weight=1)

        self._grip_label = ctk.CTkLabel(
            self,
            text="⠿",
            width=20,
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED,
            cursor="hand2",
        )
        self._grip_label.grid(row=0, column=0, padx=(8, 2), pady=6)

        self.timer_label = ctk.CTkLabel(
            self,
            text=WAITING_DISPLAY,
            width=48,
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.timer_label.grid(row=0, column=1, padx=(0, 8), pady=6, sticky="w")

        self._name_label = ctk.CTkLabel(
            self,
            text=self._chest_label(language),
            width=52,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self._name_label.grid(row=0, column=2, padx=(0, 8), pady=6, sticky="w")

        self._map_label_widget = ctk.CTkLabel(
            self,
            text=self._map_label or "—",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self._map_label_widget.grid(row=0, column=3, padx=(0, 10), pady=6, sticky="ew")

        self._grip_label.bind("<ButtonPress-1>", self._handle_drag_start, add="+")
        self._grip_label.bind("<B1-Motion>", self._handle_drag_motion, add="+")
        self._grip_label.bind("<ButtonRelease-1>", self._handle_drag_end, add="+")

    def _chest_label(self, language: Language) -> str:
        return chest_display_label(self._timer_key, language=language, short=True)

    @property
    def timer_key(self) -> TimerKey:
        return self._timer_key

    def set_duration_minutes(self, duration_minutes: float) -> None:
        self._duration_seconds = max(1.0, duration_minutes * 60.0)

    def set_map_label(self, map_label: str | None) -> None:
        self._map_label = map_label
        self._map_label_widget.configure(text=map_label or "—")

    def set_language(self, language: Language) -> None:
        self._language = language
        self._name_label.configure(text=self._chest_label(language))
        self._refresh()

    def set_drop_highlight(self, active: bool) -> None:
        self.configure(border_color=TIMER_ACTIVE if active else BORDER)

    def set_dragging(self, active: bool) -> None:
        self.configure(fg_color=BG_ELEVATED if active else BG_INSET)

    @property
    def is_counting(self) -> bool:
        return self._expires_at is not None

    def capture_state(self) -> tuple[float | None, bool]:
        return self._expires_at, self._expired

    def restore_state(self, expires_at: float | None, expired: bool) -> None:
        self._expires_at = expires_at
        self._expired = expired
        self._refresh()

    def _handle_drag_start(self, event) -> None:
        if self._on_drag_start is not None:
            self._on_drag_start(self)

    def _handle_drag_motion(self, event) -> None:
        if self._on_drag_motion is not None:
            self._on_drag_motion(self, event)

    def _handle_drag_end(self, _event) -> None:
        if self._on_drag_end is not None:
            self._on_drag_end(self)

    def start_countdown(self) -> None:
        self._expired = False
        self._expires_at = time.time() + self._duration_seconds
        play_chest_drop_sound()
        self._refresh()

    def start_countdown_on_drop(self) -> bool:
        if self.is_counting:
            return False
        self.start_countdown()
        return True

    def reset(self) -> None:
        self._expires_at = None
        self._expired = False
        self._refresh()

    def tick(self) -> None:
        if self._expired or self._expires_at is not None:
            self._refresh()

    def _refresh(self) -> None:
        if self._expired:
            self.timer_label.configure(text=EXPIRED_DISPLAY, text_color=DANGER)
            return

        if self._expires_at is None:
            self.timer_label.configure(text=WAITING_DISPLAY, text_color=TIMER_WAITING)
            return

        remaining = self._expires_at - time.time()
        if remaining <= 0:
            self._expires_at = None
            self._expired = True
            self.timer_label.configure(text=EXPIRED_DISPLAY, text_color=DANGER)
            play_timer_expired_sound()
            return

        self.timer_label.configure(
            text=_format_countdown(int(remaining)),
            text_color=TIMER_ACTIVE,
        )


class ChestTimerBoard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        duration_minutes: float = 12.0,
        language: Language = Language.PT_BR,
        on_order_changed: Callable[[list[int]], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=BG_SURFACE,
            corner_radius=RADIUS_PANEL,
            border_width=1,
            border_color=BORDER_SUBTLE,
            **kwargs,
        )
        self._duration_minutes = duration_minutes
        self._language = language
        self._on_order_changed = on_order_changed
        self._watch_targets: list[TimerWatchTarget] = []
        self._order: list[TimerKey] = []
        self._rows: dict[TimerKey, ChestTimerRow] = {}
        self._dragging_key: TimerKey | None = None
        self._syncing_order = False

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER, PAD_TIGHT))

        self.title_label = section_label(
            header,
            text=t("chest_timers_title", language=language),
        )
        self.title_label.pack(side="left")

        self.hint_label = hint_label(
            header,
            text=t("timers_drag_hint", language=language),
        )
        self.hint_label.pack(side="right")

        self.empty_label = hint_label(
            self,
            text=t("timers_none_enabled", language=language),
            wraplength=320,
            justify="left",
        )

        self.rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=PAD_INNER, pady=(0, PAD_INNER))
        self.rows_frame.grid_columnconfigure(0, weight=1)

    def set_duration_minutes(self, duration_minutes: float) -> None:
        self._duration_minutes = duration_minutes
        for row in self._rows.values():
            row.set_duration_minutes(duration_minutes)

    def set_language(self, language: Language) -> None:
        self._language = language
        self.title_label.configure(text=t("chest_timers_title", language=language))
        self.hint_label.configure(text=t("timers_drag_hint", language=language))
        self.empty_label.configure(text=t("timers_none_enabled", language=language))
        for row in self._rows.values():
            row.set_language(language)
        self._refresh_map_labels()

    def set_watch_targets(self, slots: list[ChestFarmSlot]) -> None:
        self._watch_targets = [
            TimerWatchTarget(
                chest_level=slot.chest_level,
                stage_key=slot.stage_key,
                priority=slot.priority,
            )
            for slot in sorted(slots, key=lambda item: item.priority)
        ]
        self._merge_order_from_slots(slots)
        self._rebuild_rows()

    def _merge_order_from_slots(self, slots: list[ChestFarmSlot]) -> None:
        slot_levels = [
            slot.chest_level for slot in sorted(slots, key=lambda item: item.priority)
        ]
        slot_level_set = set(slot_levels)

        if not self._order:
            merged: list[TimerKey] = list(slot_levels)
        else:
            merged = [key for key in self._order if key in slot_level_set]
            for level in slot_levels:
                if level not in merged:
                    merged.append(level)

        self._order = merged

    def _target_for_key(self, timer_key: TimerKey) -> TimerWatchTarget | None:
        for target in self._watch_targets:
            if target.chest_level == timer_key:
                return target
        return None

    def _map_label_for_key(self, timer_key: TimerKey) -> str | None:
        target = self._target_for_key(timer_key)
        if target is None or target.stage_key <= 0:
            return None
        return format_watch_map_label_for_stage_key(target.stage_key, language=self._language)

    def _refresh_map_labels(self) -> None:
        for timer_key, row in self._rows.items():
            row.set_map_label(self._map_label_for_key(timer_key))

    def _layout_rows(self) -> None:
        for index, timer_key in enumerate(self._order):
            row = self._rows.get(timer_key)
            if row is None:
                continue
            row.grid(row=index, column=0, sticky="ew", pady=3)

    def _rebuild_rows(self) -> None:
        preserved: dict[TimerKey, tuple[float | None, bool]] = {}
        for key, row in self._rows.items():
            preserved[key] = row.capture_state()

        for row in self._rows.values():
            row.destroy()
        self._rows.clear()
        self.empty_label.pack_forget()
        self.rows_frame.pack_forget()

        if not self._order:
            self.empty_label.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)
            return

        self.rows_frame.pack(fill="both", expand=True, padx=PAD_INNER, pady=(0, PAD_INNER))
        for timer_key in self._order:
            row = ChestTimerRow(
                self.rows_frame,
                timer_key=timer_key,
                duration_minutes=self._duration_minutes,
                map_label=self._map_label_for_key(timer_key),
                language=self._language,
                on_drag_start=self._on_row_drag_start,
                on_drag_motion=self._on_row_drag_motion,
                on_drag_end=self._on_row_drag_end,
            )
            self._rows[timer_key] = row
            if timer_key in preserved:
                expires_at, expired = preserved[timer_key]
                row.restore_state(expires_at, expired)

        self._layout_rows()

    def _on_row_drag_start(self, row: ChestTimerRow) -> None:
        self._dragging_key = row.timer_key
        row.set_dragging(True)

    def _on_row_drag_motion(self, _row: ChestTimerRow, event) -> None:
        if self._dragging_key is None:
            return

        drop_key = self._row_at_position(event.x_root, event.y_root)
        for timer_key, timer_row in self._rows.items():
            timer_row.set_drop_highlight(
                drop_key == timer_key and timer_key != self._dragging_key
            )

    def apply_level_order(self, levels: list[int]) -> None:
        self._syncing_order = True
        try:
            merged = list(levels)
            for key in self._order:
                if key not in merged:
                    merged.append(key)
            self._order = merged
            self._layout_rows()
        finally:
            self._syncing_order = False

    def _row_at_position(self, x_root: int, y_root: int) -> TimerKey | None:
        for timer_key, row in self._rows.items():
            try:
                left = row.winfo_rootx()
                top = row.winfo_rooty()
                right = left + row.winfo_width()
                bottom = top + row.winfo_height()
            except Exception:
                continue
            if left <= x_root <= right and top <= y_root <= bottom:
                return timer_key
        return None

    def _on_row_drag_end(self, _row: ChestTimerRow) -> None:
        if self._dragging_key is None:
            return

        dragging_key = self._dragging_key
        self._dragging_key = None

        for timer_row in self._rows.values():
            timer_row.set_drop_highlight(False)
            timer_row.set_dragging(False)

        drop_key = self._row_at_position(self.winfo_pointerx(), self.winfo_pointery())
        if drop_key is None or drop_key == dragging_key:
            return

        from_index = self._order.index(dragging_key)
        to_index = self._order.index(drop_key)
        self._order.pop(from_index)
        self._order.insert(to_index, dragging_key)
        self._layout_rows()
        self._emit_order_changed()

    def _emit_order_changed(self) -> None:
        if self._on_order_changed is None or self._syncing_order:
            return
        self._on_order_changed(list(self._order))

    def start_timer(self, timer_key: TimerKey) -> None:
        row = self._rows.get(timer_key)
        if row is not None:
            row.start_countdown()

    def start_timer_on_drop(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        if row is None:
            return False
        return row.start_countdown_on_drop()

    def is_timer_counting(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        return row.is_counting if row is not None else False

    def reset_all(self) -> None:
        for row in self._rows.values():
            row.reset()

    def tick(self) -> None:
        for row in self._rows.values():
            row.tick()
