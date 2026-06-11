from __future__ import annotations

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
    PAD_INNER,
    PAD_TIGHT,
    RADIUS_CARD,
    RADIUS_SMALL,
    TEXT_MUTED,
    option_menu,
    secondary_button,
    section_label,
)


def _map_option_label(entry: StageCatalogEntry, language: Language, suggested: bool) -> str:
    base = format_watch_map_label(
        act=entry.act,
        stage=entry.stage,
        difficulty=entry.difficulty,
        map_name=entry.name,
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

        self._chest_level = slot.chest_level
        self._valid_stages = stages_for_chest_level(self._chest_level)
        self._suggested = suggested_stage_for_chest_level(self._chest_level)
        self._map_labels: list[str] = []
        self._label_to_stage_key: dict[str, int] = {}

        self.grid_columnconfigure(2, weight=1)

        self._order_label = ctk.CTkLabel(
            self,
            text=f"#{index}",
            width=28,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self._order_label.grid(row=0, column=0, padx=(PAD_INNER, 6), pady=PAD_TIGHT)

        self._chest_menu = option_menu(
            self,
            values=self._chest_level_options(),
            command=self._on_chest_changed,
            width=84,
        )
        self._chest_menu.set(chest_display_label(self._chest_level, language=language, short=True))
        self._chest_menu.grid(row=0, column=1, padx=(0, 6), pady=PAD_TIGHT)

        self._map_menu = option_menu(
            self,
            values=["—"],
            command=self._on_map_changed,
            width=168,
        )
        self._map_menu.grid(row=0, column=2, sticky="ew", padx=(0, 6), pady=PAD_TIGHT)

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
        self._remove_btn.grid(row=0, column=3, padx=(0, PAD_TIGHT), pady=PAD_TIGHT)

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
        self._rebuild_map_options()
        self._select_stage_key(current_key)

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
        )


class ChestWatchPanel(ctk.CTkFrame):
    def __init__(self, master, language: Language, on_change, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self._language = language
        self._on_change = on_change
        self._rows: list[ChestWatchRow] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = section_label(self, text=t("watch_title", language=language))
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, PAD_TIGHT))

        self.rows_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=BG_INSET,
            border_width=1,
            border_color=BORDER_SUBTLE,
            corner_radius=RADIUS_CARD,
            scrollbar_button_color=BG_ELEVATED,
            scrollbar_button_hover_color=HOVER,
        )
        self.rows_scroll.grid(row=1, column=0, sticky="nsew", pady=(0, PAD_INNER))
        self.rows_scroll.grid_columnconfigure(0, weight=1)

        self.add_button = secondary_button(
            self,
            text=t("add_chest", language=language),
            command=self._add_chest,
        )
        self.add_button.grid(row=2, column=0, sticky="ew")

    def set_language(self, language: Language) -> None:
        self._language = language
        self.title_label.configure(text=t("watch_title", language=language))
        self.add_button.configure(text=t("add_chest", language=language))
        self._refresh_rows()

    def load_slots(self, slots: list[ChestFarmSlot]) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()

        active = [slot for slot in sorted(slots, key=lambda item: item.priority) if slot.enabled]
        if not active:
            active = self._default_slots()

        for index, slot in enumerate(active, start=1):
            self._append_row(index, slot)

        self._sync_row_context()
        self._refresh_add_button()

    def _default_slots(self) -> list[ChestFarmSlot]:
        defaults: list[ChestFarmSlot] = []
        for index, level in enumerate((40, 50), start=1):
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
        )
        row.grid(row=len(self._rows), column=0, sticky="ew", pady=4)
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

    def apply_level_order(self, levels: list[int]) -> None:
        row_by_level = {row.to_slot().chest_level: row for row in self._rows}
        reordered = [row_by_level[level] for level in levels if level in row_by_level]
        for row in self._rows:
            if row not in reordered:
                reordered.append(row)
        self._rows = reordered
        for index, row in enumerate(self._rows, start=1):
            row.grid(row=index - 1, column=0, sticky="ew", pady=4)
        self._sync_row_context()

    def collect_slots(self) -> list[ChestFarmSlot]:
        return [row.to_slot() for row in self._rows]

    def watched_levels(self) -> set[int]:
        return {slot.chest_level for slot in self.collect_slots()}
