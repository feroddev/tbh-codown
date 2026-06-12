from __future__ import annotations

import time
from dataclasses import dataclass

import customtkinter as ctk

from src.data.chest_catalog import chest_display_label
from src.domain.chest_farm import ChestFarmSlot
from src.domain.timer_urgency import (
    TimerSortState,
    pick_next_collectable_key,
    sort_timer_keys_by_urgency,
)
from src.ui.i18n import (
    Language,
    format_game_instruction_for_stage_key,
    format_watch_map_label_for_stage_key,
    t,
)
from src.ui.sound_notifier import play_chest_drop_sound, play_timer_expired_sound
from src.ui.theme import (
    BG_INSET,
    BG_SURFACE,
    BORDER,
    BORDER_SUBTLE,
    DANGER,
    SUCCESS,
    PAD_INNER,
    PAD_TIGHT,
    RADIUS_CARD,
    RADIUS_PANEL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    NEXT_TARGET_BORDER,
    TIMER_ACTIVE,
    TIMER_WAITING,
    WARNING,
    hint_label,
    section_label,
)

TimerKey = int
EXPIRED_DISPLAY = "0:00"
WAITING_DISPLAY = "--:--"
ROW_HEIGHT = 34


def _display_remaining_seconds(
    expires_at: float | None,
    expired: bool,
    clear_time_seconds: int,
) -> float | None:
    if expired:
        return 0.0
    if expires_at is None:
        return None
    return max(0.0, (expires_at - time.time()) - clear_time_seconds)


@dataclass(frozen=True)
class TimerWatchTarget:
    chest_level: int
    stage_key: int
    priority: int
    clear_time_seconds: int = 0


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
        clear_time_seconds: int = 0,
        priority: int = 1,
        language: Language = Language.PT_BR,
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
        self._clear_time_seconds = max(0, clear_time_seconds)
        self._expires_at: float | None = None
        self._expired = False
        self._language = language
        self._is_next_target = False
        self._priority = priority

        self.grid_columnconfigure(3, weight=1)

        self._priority_label = ctk.CTkLabel(
            self,
            text=f"{priority}#",
            width=24,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self._priority_label.grid(row=0, column=0, padx=(10, 4), pady=6, sticky="w")

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

    def _chest_label(self, language: Language) -> str:
        return chest_display_label(self._timer_key, language=language, short=True)

    @property
    def timer_key(self) -> TimerKey:
        return self._timer_key

    def set_duration_minutes(self, duration_minutes: float) -> None:
        self._duration_seconds = max(1.0, duration_minutes * 60.0)

    def set_clear_time_seconds(self, clear_time_seconds: int) -> None:
        self._clear_time_seconds = max(0, clear_time_seconds)
        self._refresh()

    def set_priority(self, priority: int) -> None:
        self._priority = priority
        self._priority_label.configure(text=f"{priority}#")

    def set_map_label(self, map_label: str | None) -> None:
        self._map_label = map_label
        self._map_label_widget.configure(text=map_label or "—")

    def set_language(self, language: Language) -> None:
        self._language = language
        self._name_label.configure(text=self._chest_label(language))
        self._refresh()

    def set_next_target_highlight(self, active: bool) -> None:
        self._is_next_target = active
        self.configure(border_color=NEXT_TARGET_BORDER if active else BORDER)

    @property
    def is_counting(self) -> bool:
        return self._expires_at is not None

    @property
    def is_expired(self) -> bool:
        return self._expired

    def capture_state(self) -> tuple[float | None, bool]:
        return self._expires_at, self._expired

    def restore_state(self, expires_at: float | None, expired: bool) -> None:
        self._expires_at = expires_at
        self._expired = expired
        self._refresh()

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

        display_remaining = _display_remaining_seconds(
            self._expires_at,
            False,
            self._clear_time_seconds,
        )
        if display_remaining is not None and display_remaining <= 0:
            self.timer_label.configure(text=EXPIRED_DISPLAY, text_color=WARNING)
            return

        self.timer_label.configure(
            text=_format_countdown(int(display_remaining or 0)),
            text_color=TIMER_ACTIVE,
        )


class ChestTimerBoard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        duration_minutes: float = 12.0,
        language: Language = Language.PT_BR,
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
        self._watch_targets: list[TimerWatchTarget] = []
        self._order: list[TimerKey] = []
        self._rows: dict[TimerKey, ChestTimerRow] = {}

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD_INNER, pady=(PAD_INNER, PAD_TIGHT))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = section_label(
            header,
            text=t("chest_timers_title", language=language),
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.next_phase_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=SUCCESS,
            anchor="w",
        )
        self.next_phase_label.grid(row=1, column=0, sticky="ew", pady=(PAD_TIGHT, 0))

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
        self.empty_label.configure(text=t("timers_none_enabled", language=language))
        for row in self._rows.values():
            row.set_language(language)
        self._refresh_map_labels()
        self._update_next_target_highlight()

    def set_watch_targets(self, slots: list[ChestFarmSlot]) -> None:
        self._watch_targets = [
            TimerWatchTarget(
                chest_level=slot.chest_level,
                stage_key=slot.stage_key,
                priority=slot.priority,
                clear_time_seconds=slot.clear_time_seconds or 0,
            )
            for slot in sorted(slots, key=lambda item: item.priority)
        ]
        self._order = [
            slot.chest_level for slot in sorted(slots, key=lambda item: item.priority)
        ]
        self._rebuild_rows()

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
            target = self._target_for_key(timer_key)
            clear_time = target.clear_time_seconds if target is not None else 0
            priority = target.priority if target is not None else 99
            row = ChestTimerRow(
                self.rows_frame,
                timer_key=timer_key,
                duration_minutes=self._duration_minutes,
                map_label=self._map_label_for_key(timer_key),
                clear_time_seconds=clear_time,
                priority=priority,
                language=self._language,
            )
            self._rows[timer_key] = row
            if timer_key in preserved:
                expires_at, expired = preserved[timer_key]
                row.restore_state(expires_at, expired)

        self._layout_rows()
        self._auto_sort_by_urgency()

    def _collect_sort_states(self) -> list[TimerSortState]:
        states: list[TimerSortState] = []
        for timer_key in self._order:
            row = self._rows.get(timer_key)
            target = self._target_for_key(timer_key)
            if row is None or target is None:
                continue
            expires_at, expired = row.capture_state()
            clear_time = target.clear_time_seconds if target is not None else 0
            states.append(
                TimerSortState(
                    timer_key=timer_key,
                    priority=target.priority,
                    expires_at=expires_at,
                    expired=expired,
                    clear_time_seconds=clear_time,
                )
            )
        return states

    def _auto_sort_by_urgency(self) -> None:
        if not self._rows:
            return

        states = self._collect_sort_states()
        new_order = sort_timer_keys_by_urgency(states)
        for timer_key in self._order:
            if timer_key not in new_order:
                new_order.append(timer_key)

        if new_order != self._order:
            self._order = new_order
            self._layout_rows()

        self._update_next_target_highlight()

    def _next_target_key(self) -> TimerKey | None:
        return pick_next_collectable_key(self._collect_sort_states())

    def _update_next_target_highlight(self) -> None:
        next_key = self._next_target_key()
        for timer_key, row in self._rows.items():
            row.set_next_target_highlight(next_key is not None and timer_key == next_key)

        if next_key is None:
            self.next_phase_label.configure(text="")
            return

        target = self._target_for_key(next_key)
        if target is None or target.stage_key <= 0:
            self.next_phase_label.configure(
                text=chest_display_label(next_key, language=self._language, short=True)
            )
            return

        instruction = format_game_instruction_for_stage_key(
            target.stage_key,
            language=self._language,
        )
        chest_label = chest_display_label(next_key, language=self._language, short=True)
        self.next_phase_label.configure(
            text=t(
                "timers_next_phase",
                language=self._language,
                instruction=instruction,
                chest=chest_label,
            )
        )

    def start_timer(self, timer_key: TimerKey) -> None:
        row = self._rows.get(timer_key)
        if row is not None:
            row.start_countdown()
            self._auto_sort_by_urgency()

    def start_timer_on_drop(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        if row is None:
            return False
        started = row.start_countdown_on_drop()
        if started:
            self._auto_sort_by_urgency()
        return started

    def is_timer_counting(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        return row.is_counting if row is not None else False

    def reset_all(self) -> None:
        for row in self._rows.values():
            row.reset()
        self._auto_sort_by_urgency()

    def tick(self) -> None:
        for row in self._rows.values():
            row.tick()
        self._auto_sort_by_urgency()
