from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk

from src.data.chest_catalog import chest_display_label
from src.domain.chest_farm import ChestFarmSlot
from src.domain.chest_timer_keys import (
    chest_level_from_timer_key,
    common_chest_timer_key,
    is_boss_chest_timer_key,
    is_common_chest_timer_key,
)
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
    BG_ELEVATED,
    BG_INSET,
    BG_SURFACE,
    BORDER,
    BORDER_SUBTLE,
    BTN_NEUTRAL,
    BTN_NEUTRAL_HOVER,
    COMMON_TIMER_ACTIVE,
    DANGER,
    PAD_INNER,
    PAD_SECTION,
    PAD_TIGHT,
    RADIUS_CARD,
    RADIUS_PANEL,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    NEXT_TARGET_BORDER,
    TIMER_ACTIVE,
    TIMER_WAITING,
    hint_label,
    secondary_button,
    section_label,
)

TimerKey = int
EXPIRED_DISPLAY = "0:00"
WAITING_DISPLAY = "--:--"
ROW_HEIGHT = 40
GROUP_PAD = 10


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
        display_name: str | None = None,
        map_label: str | None = None,
        clear_time_seconds: int = 0,
        priority: int = 1,
        language: Language = Language.PT_BR,
        is_common: bool = False,
        on_reset: Callable[[], None] | None = None,
        **kwargs,
    ) -> None:
        accent = COMMON_TIMER_ACTIVE if is_common else TIMER_ACTIVE
        super().__init__(
            master,
            fg_color=BG_ELEVATED,
            corner_radius=RADIUS_CARD,
            height=ROW_HEIGHT,
            border_width=1,
            border_color=BORDER_SUBTLE,
            **kwargs,
        )
        self.pack_propagate(False)
        self._timer_key = timer_key
        self._display_name = display_name
        self._map_label = map_label
        self._duration_seconds = max(1.0, duration_minutes * 60.0)
        self._clear_time_seconds = max(0, clear_time_seconds)
        self._expires_at: float | None = None
        self._expired = False
        self._language = language
        self._is_next_target = False
        self._priority = priority
        self._is_common = is_common
        self._active_color = accent
        self._on_reset = on_reset

        self.grid_columnconfigure(2, weight=1)

        kind_label = t("chest_kind_common" if is_common else "chest_kind_boss", language=language)
        self._kind_badge = ctk.CTkLabel(
            self,
            text=kind_label,
            width=52,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=accent,
            anchor="w",
        )
        self._kind_badge.grid(row=0, column=0, padx=(10, 6), pady=8, sticky="w")

        self.timer_label = ctk.CTkLabel(
            self,
            text=WAITING_DISPLAY,
            width=52,
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.timer_label.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="w")

        self._name_label = ctk.CTkLabel(
            self,
            text=self._chest_label(language),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self._name_label.grid(row=0, column=2, padx=(0, 8), pady=8, sticky="w")

        self._reset_button = secondary_button(
            self,
            text=t("timer_reset_short", language=language),
            width=56,
            height=26,
            command=self._handle_reset,
            font=ctk.CTkFont(family="Segoe UI", size=10),
        )
        self._reset_button.grid(row=0, column=3, padx=(0, 10), pady=8, sticky="e")

    def _chest_label(self, language: Language) -> str:
        if self._display_name is not None:
            return self._display_name
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

    def set_map_label(self, map_label: str | None) -> None:
        self._map_label = map_label

    def set_language(self, language: Language) -> None:
        self._language = language
        self._name_label.configure(text=self._chest_label(language))
        self._kind_badge.configure(
            text=t(
                "chest_kind_common" if self._is_common else "chest_kind_boss",
                language=language,
            )
        )
        self._reset_button.configure(text=t("timer_reset_short", language=language))
        self._refresh()

    def set_next_target_highlight(self, active: bool) -> None:
        self._is_next_target = active
        self.configure(border_color=NEXT_TARGET_BORDER if active else BORDER_SUBTLE)

    @property
    def is_counting(self) -> bool:
        return self._expires_at is not None and not self._expired

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

    def _handle_reset(self) -> None:
        self.reset()
        if self._on_reset is not None:
            self._on_reset()

    def tick(self) -> None:
        if self._expired or self._expires_at is not None:
            self._refresh()

    def _refresh(self) -> None:
        if self._expired:
            self.timer_label.configure(text=EXPIRED_DISPLAY, text_color=DANGER)
            if self._expires_at is not None and self._expires_at <= time.time():
                self._expires_at = None
            return

        if self._expires_at is None:
            self.timer_label.configure(text=WAITING_DISPLAY, text_color=TIMER_WAITING)
            return

        remaining = self._expires_at - time.time()
        display_remaining = _display_remaining_seconds(
            self._expires_at,
            False,
            self._clear_time_seconds,
        )

        if display_remaining is not None and display_remaining <= 0:
            if not self._expired:
                play_timer_expired_sound()
            self._expired = True
            self.timer_label.configure(text=EXPIRED_DISPLAY, text_color=DANGER)
            if remaining <= 0:
                self._expires_at = None
            return

        self.timer_label.configure(
            text=_format_countdown(int(display_remaining or 0)),
            text_color=self._active_color,
        )


class ChestLevelGroup(ctk.CTkFrame):
    def __init__(
        self,
        master,
        *,
        priority: int,
        map_label: str | None,
        language: Language,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=BG_INSET,
            corner_radius=RADIUS_CARD,
            border_width=1,
            border_color=BORDER,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=GROUP_PAD, pady=(GROUP_PAD, PAD_TIGHT))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text=f"{priority}#",
            width=28,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        ctk.CTkLabel(
            header,
            text=map_label or "—",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        self._rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._rows_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=GROUP_PAD,
            pady=(0, GROUP_PAD),
        )
        self._rows_frame.grid_columnconfigure(0, weight=1)

    def add_row(self, row: ChestTimerRow, *, index: int) -> None:
        row.grid(row=index, column=0, sticky="ew", pady=(0, 6))
        if index == 0:
            row.grid_configure(pady=(0, 6))
        else:
            row.grid_configure(pady=(0, 0))


class ChestTimerBoard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        boss_duration_minutes: float = 7.0,
        common_duration_minutes: float = 5.0,
        show_common_timer: bool = False,
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
        self._boss_duration_minutes = boss_duration_minutes
        self._common_duration_minutes = common_duration_minutes
        self._show_common_timer = show_common_timer
        self._language = language
        self._watch_targets: list[TimerWatchTarget] = []
        self._order: list[TimerKey] = []
        self._rows: dict[TimerKey, ChestTimerRow] = {}
        self._level_groups: dict[int, ChestLevelGroup] = {}
        self._counting_snapshot: dict[TimerKey, bool] = {}

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
            wraplength=420,
            justify="left",
        )

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=BTN_NEUTRAL,
            scrollbar_button_hover_color=BTN_NEUTRAL_HOVER,
        )
        self._scroll.grid_columnconfigure(0, weight=1)

    def _after_row_change(self) -> None:
        self._auto_sort_by_urgency()
        self._publish_counting_snapshot()

    def set_boss_duration_minutes(self, duration_minutes: float) -> None:
        self._boss_duration_minutes = duration_minutes
        for timer_key, row in self._rows.items():
            if is_boss_chest_timer_key(timer_key):
                row.set_duration_minutes(duration_minutes)

    def set_common_duration_minutes(self, duration_minutes: float) -> None:
        self._common_duration_minutes = duration_minutes
        for timer_key, row in self._rows.items():
            if is_common_chest_timer_key(timer_key):
                row.set_duration_minutes(duration_minutes)

    def set_show_common_timer(self, enabled: bool) -> None:
        if self._show_common_timer == enabled:
            return
        self._show_common_timer = enabled
        self._rebuild_rows()

    def set_language(self, language: Language) -> None:
        self._language = language
        self.title_label.configure(text=t("chest_timers_title", language=language))
        self.empty_label.configure(text=t("timers_none_enabled", language=language))
        for row in self._rows.values():
            row.set_language(language)
        for timer_key, row in self._rows.items():
            if not is_common_chest_timer_key(timer_key):
                continue
            level = chest_level_from_timer_key(timer_key)
            row._display_name = t(
                "common_chest_lv_short",
                language=language,
                level=level,
            )
            row._name_label.configure(text=row._chest_label(language))
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
        level = chest_level_from_timer_key(timer_key)
        for target in self._watch_targets:
            if target.chest_level == level:
                return target
        return None

    def _map_label_for_key(self, timer_key: TimerKey) -> str | None:
        target = self._target_for_key(timer_key)
        if target is None or target.stage_key <= 0:
            return None
        return format_watch_map_label_for_stage_key(target.stage_key, language=self._language)

    def is_common_timer_counting(self, chest_level: int) -> bool:
        return self._counting_snapshot.get(
            common_chest_timer_key(chest_level),
            False,
        )

    def is_boss_timer_counting(self, timer_key: TimerKey) -> bool:
        if is_common_chest_timer_key(timer_key):
            return False
        return self._counting_snapshot.get(timer_key, False)

    def _rebuild_rows(self) -> None:
        preserved: dict[TimerKey, tuple[float | None, bool]] = {}
        for key, row in self._rows.items():
            preserved[key] = row.capture_state()

        for row in self._rows.values():
            row.destroy()
        for group in self._level_groups.values():
            group.destroy()
        self._rows.clear()
        self._level_groups.clear()
        self.empty_label.pack_forget()
        self._scroll.pack_forget()

        if not self._order:
            self.empty_label.pack(fill="x", padx=PAD_INNER, pady=PAD_INNER)
            return

        self._scroll.pack(
            fill="both",
            expand=True,
            padx=PAD_INNER,
            pady=(0, PAD_SECTION),
        )

        for group_index, timer_key in enumerate(self._order):
            target = self._target_for_key(timer_key)
            clear_time = target.clear_time_seconds if target is not None else 0
            priority = target.priority if target is not None else 99
            map_label = self._map_label_for_key(timer_key)

            group = ChestLevelGroup(
                self._scroll,
                priority=priority,
                map_label=map_label,
                language=self._language,
            )
            group.grid(row=group_index, column=0, sticky="ew", pady=(0, PAD_SECTION))
            self._level_groups[timer_key] = group

            row_index = 0
            if self._show_common_timer:
                common_key = common_chest_timer_key(timer_key)
                common_row = ChestTimerRow(
                    group._rows_frame,
                    timer_key=common_key,
                    duration_minutes=self._common_duration_minutes,
                    display_name=t(
                        "common_chest_lv_short",
                        language=self._language,
                        level=timer_key,
                    ),
                    priority=priority,
                    language=self._language,
                    is_common=True,
                    on_reset=self._after_row_change,
                )
                self._rows[common_key] = common_row
                if common_key in preserved:
                    expires_at, expired = preserved[common_key]
                    common_row.restore_state(expires_at, expired)
                group.add_row(common_row, index=row_index)
                row_index += 1

            boss_row = ChestTimerRow(
                group._rows_frame,
                timer_key=timer_key,
                duration_minutes=self._boss_duration_minutes,
                map_label=map_label,
                clear_time_seconds=clear_time,
                priority=priority,
                language=self._language,
                is_common=False,
                on_reset=self._after_row_change,
            )
            self._rows[timer_key] = boss_row
            if timer_key in preserved:
                expires_at, expired = preserved[timer_key]
                boss_row.restore_state(expires_at, expired)
            group.add_row(boss_row, index=row_index)

        self._after_row_change()

    def _publish_counting_snapshot(self) -> None:
        self._counting_snapshot = {
            timer_key: row.is_counting for timer_key, row in self._rows.items()
        }

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
            for index, timer_key in enumerate(self._order):
                group = self._level_groups.get(timer_key)
                if group is not None:
                    group.grid(row=index, column=0, sticky="ew", pady=(0, PAD_SECTION))

        self._update_next_target_highlight()

    def _next_target_key(self) -> TimerKey | None:
        return pick_next_collectable_key(self._collect_sort_states())

    def _update_next_target_highlight(self) -> None:
        next_key = self._next_target_key()
        for timer_key, row in self._rows.items():
            row.set_next_target_highlight(
                next_key is not None
                and timer_key == next_key
                and is_boss_chest_timer_key(timer_key)
            )

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

    def start_timer(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        if row is None:
            return False
        row.start_countdown()
        self._after_row_change()
        return True

    def start_timer_on_drop(self, timer_key: TimerKey) -> bool:
        row = self._rows.get(timer_key)
        if row is None:
            return False
        started = row.start_countdown_on_drop()
        if started:
            self._after_row_change()
        return started

    def has_timer_row(self, timer_key: TimerKey) -> bool:
        return timer_key in self._rows

    def is_timer_counting(self, timer_key: TimerKey) -> bool:
        return self._counting_snapshot.get(timer_key, False)

    def reset_all(self) -> None:
        for row in self._rows.values():
            row.reset()
        self._after_row_change()

    def tick(self) -> None:
        for row in self._rows.values():
            row.tick()
        self._after_row_change()
