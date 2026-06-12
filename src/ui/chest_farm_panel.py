from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from src.data.chest_catalog import boss_farm_levels, chest_display_label
from src.data.stage_catalog import (
    StageCatalogEntry,
    stages_for_chest_level,
    suggested_stage_for_chest_level,
)
from src.domain.chest_farm import ChestFarmSlot
from src.ui.i18n import Language, format_watch_map_label, t
from src.ui.theme import (
    BG_ELEVATED,
    BG_INSET,
    BORDER,
    BORDER_SUBTLE,
    DANGER,
    DANGER_HOVER,
    HOVER,
    LEFT_PANEL_MIN_WIDTH,
    PAD_INNER,
    PAD_TIGHT,
    RADIUS_CARD,
    RADIUS_SMALL,
    SWITCH_PROGRESS,
    TEXT_MUTED,
    hint_label,
    option_menu,
    secondary_button,
    section_label,
)

LEFT_PANEL_HINT_WIDTH = LEFT_PANEL_MIN_WIDTH - 56


def _map_option_label(entry: StageCatalogEntry, language: Language, suggested: bool) -> str:
    base = format_watch_map_label(
        act=entry.act,
        stage=entry.stage,
        difficulty=entry.difficulty,
        boss_drop_percent=entry.boss_chest_drop_percent,
        language=language,
    )
    if suggested:
        return f"★ {base}"
    return base


class ChestWatchRow(ctk.CTkFrame):
    def __init__(
        self,
        master,
        index: int,
        slot: ChestFarmSlot,
        language: Language,
        used_levels: set[int],
        on_change,
        on_remove,
        can_remove: bool,
        on_drag_start: Callable[["ChestWatchRow"], None] | None = None,
        on_drag_motion: Callable[["ChestWatchRow", object], None] | None = None,
        on_drag_end: Callable[["ChestWatchRow"], None] | None = None,
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
        self._index = index
        self._slot = slot
        self._language = language
        self._used_levels = used_levels
        self._on_change = on_change
        self._on_remove = on_remove
        self._on_drag_start = on_drag_start
        self._on_drag_motion = on_drag_motion
        self._on_drag_end = on_drag_end
        self._last_clear_time_seconds = slot.clear_time_seconds

        self._chest_level = slot.chest_level
        self._valid_stages = stages_for_chest_level(self._chest_level)
        self._suggested = suggested_stage_for_chest_level(self._chest_level)
        self._map_labels: list[str] = []
        self._label_to_stage_key: dict[str, int] = {}

        self.grid_columnconfigure(3, weight=1)

        self._grip_label = ctk.CTkLabel(
            self,
            text="⠿",
            width=20,
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED,
            cursor="hand2",
        )
        self._grip_label.grid(row=0, column=0, padx=(PAD_TIGHT, 2), pady=PAD_TIGHT)

        self._order_label = ctk.CTkLabel(
            self,
            text=f"#{index}",
            width=28,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self._order_label.grid(row=0, column=1, padx=(0, 6), pady=PAD_TIGHT)

        self._chest_menu = option_menu(
            self,
            values=self._chest_level_options(),
            command=self._on_chest_changed,
            width=84,
        )
        self._chest_menu.set(chest_display_label(self._chest_level, language=language, short=True))
        self._chest_menu.grid(row=0, column=2, padx=(0, 6), pady=PAD_TIGHT)

        self._map_menu = option_menu(
            self,
            values=["—"],
            command=self._on_map_changed,
            width=168,
        )
        self._map_menu.grid(row=0, column=3, sticky="ew", padx=(0, 6), pady=PAD_TIGHT)

        self._clear_time_entry = ctk.CTkEntry(
            self,
            width=52,
            height=30,
            justify="center",
            corner_radius=RADIUS_SMALL,
            border_width=1,
            border_color=BORDER,
            fg_color=BG_ELEVATED,
            placeholder_text=t("watch_clear_time_placeholder", language=language),
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self._clear_time_entry.grid(row=0, column=4, padx=(0, 6), pady=PAD_TIGHT)
        self._clear_time_entry.bind("<Return>", self._on_clear_time_commit)
        self._clear_time_entry.bind("<FocusOut>", self._on_clear_time_commit)
        self._set_clear_time_value(slot.clear_time_seconds)

        self._remove_btn = ctk.CTkButton(
            self,
            text="×",
            width=30,
            height=30,
            corner_radius=RADIUS_SMALL,
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            border_width=0,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._on_remove_clicked,
            state="normal" if can_remove else "disabled",
        )
        self._remove_btn.grid(row=0, column=5, padx=(0, PAD_TIGHT), pady=PAD_TIGHT)

        self._grip_label.bind("<ButtonPress-1>", self._handle_drag_start, add="+")
        self._grip_label.bind("<B1-Motion>", self._handle_drag_motion, add="+")
        self._grip_label.bind("<ButtonRelease-1>", self._handle_drag_end, add="+")

        self._rebuild_map_options()
        self._select_stage_key(slot.stage_key)

    def _chest_level_options(self) -> list[str]:
        options: list[str] = []
        for level in boss_farm_levels():
            if level == self._chest_level or level not in self._used_levels:
                options.append(chest_display_label(level, language=self._language, short=True))
        return options or [chest_display_label(self._chest_level, language=self._language, short=True)]

    def _level_from_label(self, label: str) -> int | None:
        for level in boss_farm_levels():
            if chest_display_label(level, language=self._language, short=True) == label:
                return level
        return None

    def set_language(self, language: Language) -> None:
        self._language = language
        current_key = self.to_slot().stage_key
        self._chest_menu.configure(values=self._chest_level_options())
        self._chest_menu.set(
            chest_display_label(self._chest_level, language=language, short=True)
        )
        self._clear_time_entry.configure(
            placeholder_text=t("watch_clear_time_placeholder", language=language)
        )
        self._rebuild_map_options()
        self._select_stage_key(current_key)

    def _set_clear_time_value(self, seconds: int | None) -> None:
        self._clear_time_entry.delete(0, "end")
        if seconds is not None:
            self._clear_time_entry.insert(0, str(seconds))

    def _parse_clear_time_seconds(self) -> int | None:
        raw = self._clear_time_entry.get().strip()
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        if value < 0 or value > 9999:
            return None
        return value

    def _on_clear_time_commit(self, _event=None) -> None:
        parsed = self._parse_clear_time_seconds()
        raw = self._clear_time_entry.get().strip()
        if raw and parsed is None:
            self._set_clear_time_value(self._last_clear_time_seconds)
            return
        self._last_clear_time_seconds = parsed
        if parsed is not None:
            self._set_clear_time_value(parsed)
        self._on_change()

    @property
    def chest_level(self) -> int:
        return self._chest_level

    def set_drop_highlight(self, active: bool) -> None:
        self.configure(border_color=SWITCH_PROGRESS if active else BORDER)

    def set_dragging(self, active: bool) -> None:
        self.configure(fg_color=BG_ELEVATED if active else BG_INSET)

    def _handle_drag_start(self, event) -> None:
        if self._on_drag_start is not None:
            self._on_drag_start(self)

    def _handle_drag_motion(self, event) -> None:
        if self._on_drag_motion is not None:
            self._on_drag_motion(self, event)

    def _handle_drag_end(self, _event) -> None:
        if self._on_drag_end is not None:
            self._on_drag_end(self)

    def update_context(self, index: int, used_levels: set[int], can_remove: bool) -> None:
        self._index = index
        self._used_levels = used_levels
        self._order_label.configure(text=f"#{index}")
        self._chest_menu.configure(values=self._chest_level_options())
        self._remove_btn.configure(state="normal" if can_remove else "disabled")

    def _rebuild_map_options(self) -> None:
        self._valid_stages = stages_for_chest_level(self._chest_level)
        self._suggested = suggested_stage_for_chest_level(self._chest_level)
        self._map_labels.clear()
        self._label_to_stage_key.clear()

        if not self._valid_stages:
            placeholder = t("no_maps_for_chest", language=self._language)
            self._map_menu.configure(values=[placeholder])
            self._map_menu.set(placeholder)
            return

        suggested_key = self._suggested.stage_key if self._suggested else None
        for entry in self._valid_stages:
            label = _map_option_label(
                entry,
                self._language,
                suggested=entry.stage_key == suggested_key,
            )
            self._map_labels.append(label)
            self._label_to_stage_key[label] = entry.stage_key

        self._map_menu.configure(values=self._map_labels)

    def _select_stage_key(self, stage_key: int) -> None:
        for label, key in self._label_to_stage_key.items():
            if key == stage_key:
                self._map_menu.set(label)
                return
        if self._suggested is not None:
            for label, key in self._label_to_stage_key.items():
                if key == self._suggested.stage_key:
                    self._map_menu.set(label)
                    return

    def _on_chest_changed(self, label: str) -> None:
        level = self._level_from_label(label)
        if level is None or level == self._chest_level:
            return
        self._chest_level = level
        self._rebuild_map_options()
        if self._suggested is not None:
            self._select_stage_key(self._suggested.stage_key)
        self._on_change()

    def _on_map_changed(self, _label: str) -> None:
        self._on_change()

    def _on_remove_clicked(self) -> None:
        self._on_remove(self)

    def to_slot(self) -> ChestFarmSlot:
        stage_key = self._slot.stage_key
        selected_map = self._map_menu.get()
        if selected_map in self._label_to_stage_key:
            stage_key = self._label_to_stage_key[selected_map]
        elif self._suggested is not None:
            stage_key = self._suggested.stage_key

        return ChestFarmSlot(
            chest_level=self._chest_level,
            stage_key=stage_key,
            enabled=True,
            priority=self._index,
            clear_time_seconds=self._parse_clear_time_seconds(),
        )


class ChestWatchPanel(ctk.CTkFrame):
    def __init__(self, master, language: Language, on_change, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self._language = language
        self._on_change = on_change
        self._rows: list[ChestWatchRow] = []
        self._dragging_row: ChestWatchRow | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PAD_TIGHT))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = section_label(header, text=t("watch_title", language=language))
        self.title_label.grid(row=0, column=0, sticky="w")

        self.hint_label = hint_label(
            header,
            text=t("watch_drag_hint", language=language),
        )
        self.hint_label.grid(row=0, column=1, sticky="e")

        self.clear_time_hint_label = hint_label(
            self,
            text=t("watch_clear_time_hint", language=language),
            wraplength=LEFT_PANEL_HINT_WIDTH,
            justify="left",
        )
        self.clear_time_hint_label.grid(row=1, column=0, sticky="ew", pady=(0, PAD_TIGHT))

        self.rows_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_INSET,
            border_width=1,
            border_color=BORDER_SUBTLE,
            corner_radius=RADIUS_CARD,
            scrollbar_button_color=BG_ELEVATED,
            scrollbar_button_hover_color=HOVER,
        )
        self.rows_scroll.grid(row=2, column=0, sticky="nsew", pady=(0, PAD_INNER))
        self.rows_scroll.grid_columnconfigure(0, weight=1)
        self._build_columns_header()

        self.add_button = secondary_button(
            self,
            text=t("add_chest", language=language),
            command=self._add_chest,
        )
        self.add_button.grid(row=3, column=0, sticky="ew")

    def _build_columns_header(self) -> None:
        if hasattr(self, "_columns_header"):
            self._columns_header.destroy()

        self._columns_header = ctk.CTkFrame(self.rows_scroll, fg_color="transparent")
        self._columns_header.grid(row=0, column=0, sticky="ew", padx=(PAD_TIGHT, PAD_TIGHT), pady=(4, 0))
        self._columns_header.grid_columnconfigure(3, weight=1)

        header_font = ctk.CTkFont(family="Segoe UI", size=10, weight="bold")

        ctk.CTkLabel(self._columns_header, text="#", width=28, font=header_font, text_color=TEXT_MUTED).grid(
            row=0, column=1, padx=(0, 6)
        )
        ctk.CTkLabel(
            self._columns_header,
            text=t("watch_header_chest", language=self._language),
            width=84,
            font=header_font,
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=2, padx=(0, 6), sticky="w")
        ctk.CTkLabel(
            self._columns_header,
            text=t("watch_header_map", language=self._language),
            font=header_font,
            text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=3, padx=(0, 6), sticky="w")
        ctk.CTkLabel(
            self._columns_header,
            text=t("watch_clear_time", language=self._language),
            width=52,
            font=header_font,
            text_color=TEXT_MUTED,
            anchor="center",
        ).grid(row=0, column=4, padx=(0, 6))

    def set_language(self, language: Language) -> None:
        self._language = language
        self.title_label.configure(text=t("watch_title", language=language))
        self.hint_label.configure(text=t("watch_drag_hint", language=language))
        self.clear_time_hint_label.configure(
            text=t("watch_clear_time_hint", language=language)
        )
        self.add_button.configure(text=t("add_chest", language=language))
        self._build_columns_header()
        self._refresh_rows()

    def load_slots(self, slots: list[ChestFarmSlot]) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()

        active = [slot for slot in sorted(slots, key=lambda item: item.priority) if slot.enabled]
        if not active:
            active = self._default_slots()

        seen_levels: set[int] = set()
        unique_slots: list[ChestFarmSlot] = []
        for slot in active:
            if slot.chest_level in seen_levels:
                continue
            seen_levels.add(slot.chest_level)
            unique_slots.append(slot)
        active = unique_slots

        for index, slot in enumerate(active, start=1):
            self._append_row(index, slot)

        self._sync_row_context()
        self._refresh_add_button()

    def _default_slots(self) -> list[ChestFarmSlot]:
        defaults: list[ChestFarmSlot] = []
        for index, level in enumerate((65, 50, 40, 30), start=1):
            suggested = suggested_stage_for_chest_level(level)
            defaults.append(
                ChestFarmSlot(
                    chest_level=level,
                    stage_key=suggested.stage_key if suggested else 0,
                    enabled=True,
                    priority=index,
                )
            )
        return defaults

    def _used_levels(self, exclude_row: ChestWatchRow | None = None) -> set[int]:
        levels: set[int] = set()
        for row in self._rows:
            if row is exclude_row:
                continue
            levels.add(row.to_slot().chest_level)
        return levels

    def _append_row(self, index: int, slot: ChestFarmSlot) -> None:
        row = ChestWatchRow(
            self.rows_scroll,
            index=index,
            slot=slot,
            language=self._language,
            used_levels=self._used_levels(),
            on_change=self._notify_change,
            on_remove=self._remove_row,
            can_remove=False,
            on_drag_start=self._on_row_drag_start,
            on_drag_motion=self._on_row_drag_motion,
            on_drag_end=self._on_row_drag_end,
        )
        row.grid(row=len(self._rows) + 1, column=0, sticky="ew", pady=4)
        self._rows.append(row)

    def _refresh_rows(self) -> None:
        slots = self.collect_slots()
        self.load_slots(slots)

    def _refresh_add_button(self) -> None:
        used = self._used_levels()
        all_levels = set(boss_farm_levels())
        can_add = len(used) < len(all_levels)
        self.add_button.configure(state="normal" if can_add else "disabled")

    def _notify_change(self) -> None:
        self._sync_row_context()
        self._refresh_add_button()
        self._on_change()

    def _sync_row_context(self) -> None:
        can_remove = len(self._rows) > 1
        for index, row in enumerate(self._rows, start=1):
            row.update_context(
                index=index,
                used_levels=self._used_levels(exclude_row=row),
                can_remove=can_remove,
            )

    def _add_chest(self) -> None:
        used = self._used_levels()
        next_level = next((level for level in boss_farm_levels() if level not in used), None)
        if next_level is None:
            return

        suggested = suggested_stage_for_chest_level(next_level)
        slot = ChestFarmSlot(
            chest_level=next_level,
            stage_key=suggested.stage_key if suggested else 0,
            enabled=True,
            priority=len(self._rows) + 1,
        )
        self._append_row(len(self._rows) + 1, slot)
        self._sync_row_context()
        self._refresh_add_button()
        self._on_change()

    def _remove_row(self, row: ChestWatchRow) -> None:
        if len(self._rows) <= 1:
            return
        row.destroy()
        self._rows.remove(row)
        self._sync_row_context()
        self._refresh_add_button()
        self._on_change()

    def _layout_rows(self) -> None:
        for index, row in enumerate(self._rows):
            row.grid(row=index + 1, column=0, sticky="ew", pady=4)

    def _row_at_position(self, x_root: int, y_root: int) -> ChestWatchRow | None:
        for row in self._rows:
            try:
                left = row.winfo_rootx()
                top = row.winfo_rooty()
                right = left + row.winfo_width()
                bottom = top + row.winfo_height()
            except Exception:
                continue
            if left <= x_root <= right and top <= y_root <= bottom:
                return row
        return None

    def _on_row_drag_start(self, row: ChestWatchRow) -> None:
        self._dragging_row = row
        row.set_dragging(True)

    def _on_row_drag_motion(self, _row: ChestWatchRow, event) -> None:
        if self._dragging_row is None:
            return

        drop_row = self._row_at_position(event.x_root, event.y_root)
        for candidate in self._rows:
            candidate.set_drop_highlight(
                drop_row is candidate and candidate is not self._dragging_row
            )

    def _on_row_drag_end(self, _row: ChestWatchRow) -> None:
        if self._dragging_row is None:
            return

        dragging_row = self._dragging_row
        self._dragging_row = None

        for candidate in self._rows:
            candidate.set_drop_highlight(False)
            candidate.set_dragging(False)

        drop_row = self._row_at_position(self.winfo_pointerx(), self.winfo_pointery())
        if drop_row is None or drop_row is dragging_row:
            return

        from_index = self._rows.index(dragging_row)
        to_index = self._rows.index(drop_row)
        self._rows.pop(from_index)
        self._rows.insert(to_index, dragging_row)
        self._layout_rows()
        self._sync_row_context()
        self._notify_change()

    def collect_slots(self) -> list[ChestFarmSlot]:
        return [row.to_slot() for row in self._rows]

    def watched_levels(self) -> set[int]:
        return {slot.chest_level for slot in self.collect_slots()}
