from __future__ import annotations

import logging
import queue
import threading
from dataclasses import replace
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from src.application.monitor_service import MonitorService
from src.config_loader import AppConfig, load_config, save_config
from src.domain.chest_event import ChestType
from src.domain.chest_timer_keys import common_chest_timer_key
from src.domain.confirmed_drop_notification import ConfirmedDropNotification
from src.domain.chest_farm import enabled_farm_maps
from src.runtime_paths import app_icon_path
from src.ui.chest_farm_panel import ChestWatchPanel
from src.ui.chest_timer import ChestTimerBoard
from src.ui.i18n import (
    Language,
    difficulty_display_name,
    format_current_stage_label,
    set_language,
    t,
)
from src.ui.theme import (
    BG_INSET,
    BG_ROOT,
    BG_SURFACE,
    BORDER,
    BTN_NEUTRAL,
    BTN_NEUTRAL_HOVER,
    ACCENT,
    ACCENT_HOVER,
    DANGER,
    DANGER_HOVER,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    DROPS_PANEL_WIDTH,
    GAP_PANEL,
    HOVER,
    PAD_INNER,
    PAD_SECTION,
    PAD_TIGHT,
    PAD_WINDOW,
    SUCCESS,
    SWITCH_PROGRESS,
    TEXT_MUTED,
    TEXT_SECONDARY,
    header_nav_cluster,
    apply_root_window,
    hint_label,
    log_textbox,
    nav_option_menu,
    option_menu,
    panel_frame,
    primary_button,
    section_label,
)


logger = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

LANGUAGE_OPTIONS = {
    "Português (BR)": Language.PT_BR,
    "English": Language.EN,
}


class MonitorApp(ctk.CTk):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        apply_root_window(self)
        self.config_path = config_path
        self.config = load_config(config_path)
        set_language(self.config.language)
        self._language = self.config.language
        self._monitor_thread: threading.Thread | None = None
        self._monitor_service: MonitorService | None = None
        self._drop_log_queue: queue.Queue[str] = queue.Queue()
        self._confirmed_drop_queue: queue.Queue[ConfirmedDropNotification] = queue.Queue()
        self._stage_key_queue: queue.Queue[int] = queue.Queue()
        self._current_stage_key: int | None = None
        self._window_size_job: str | None = None
        self._ui_ready = False
        self._current_tab = "monitor"
        self._tab_monitor_label = t("tab_monitor")
        self._tab_config_label = t("tab_config")

        self.title(t("app_title"))
        window_width = max(self.config.window_width, DEFAULT_WINDOW_WIDTH)
        window_height = max(self.config.window_height, DEFAULT_WINDOW_HEIGHT)
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self._apply_window_icon()
        self.bind("<Configure>", self._on_window_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._build_ui()
        self._load_watch_slots()
        self._sync_timers()
        self._refresh_status_labels()
        self.after(200, self._poll_queues)
        self.after(250, self._tick_timers)
        self.after(350, self._poll_current_stage)
        self.after(0, self._start_monitor)
        self.after(150, self._mark_ui_ready)

    def _build_duration_entry(
        self,
        parent,
        variable: ctk.StringVar,
        label_text: str,
        commit_handler,
    ) -> None:
        entry = ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=48,
            height=28,
            justify="center",
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
            fg_color=BG_INSET,
        )
        entry.pack(side="right", padx=(PAD_TIGHT, 0))
        entry.bind("<Return>", commit_handler)
        entry.bind("<FocusOut>", commit_handler)

        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
        )
        label.pack(side="right", padx=(PAD_TIGHT, 0))

    def _mark_ui_ready(self) -> None:
        self._ui_ready = True

    def _on_window_configure(self, event) -> None:
        if event.widget is not self or not self._ui_ready:
            return
        if self._window_size_job is not None:
            self.after_cancel(self._window_size_job)
        self._window_size_job = self.after(400, self._persist_window_size)

    def _persist_window_size(self) -> None:
        self._window_size_job = None
        width = self.winfo_width()
        height = self.winfo_height()
        if width < DEFAULT_WINDOW_WIDTH or height < DEFAULT_WINDOW_HEIGHT:
            return
        if width == self.config.window_width and height == self.config.window_height:
            return
        self.config = replace(self.config, window_width=width, window_height=height)
        save_config(self.config_path, self.config)

    def _on_window_close(self) -> None:
        if self._window_size_job is not None:
            self.after_cancel(self._window_size_job)
            self._window_size_job = None
        width = max(self.winfo_width(), DEFAULT_WINDOW_WIDTH)
        height = max(self.winfo_height(), DEFAULT_WINDOW_HEIGHT)
        if width != self.config.window_width or height != self.config.window_height:
            self.config = replace(self.config, window_width=width, window_height=height)
            save_config(self.config_path, self.config)
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitor()
        self.destroy()

    def _apply_window_icon(self) -> None:
        icon_path = app_icon_path()
        if icon_path is None:
            return
        try:
            self.iconbitmap(default=str(icon_path))
        except Exception:
            logger.debug("Could not set window icon from %s", icon_path, exc_info=True)

    def _build_ui(self) -> None:
        root = ctk.CTkFrame(self, fg_color=BG_ROOT, corner_radius=0)
        root.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        pad = PAD_WINDOW
        gap = GAP_PANEL

        header = panel_frame(root, fg_color=BG_SURFACE)
        header.grid(row=0, column=0, sticky="ew", padx=pad, pady=(pad, gap))
        header.grid_columnconfigure(0, weight=1)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=PAD_INNER, pady=PAD_SECTION)

        title_block = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_block.pack(side="left")

        self.sidebar_title_label = section_label(
            title_block,
            text=t("app_title"),
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        )
        self.sidebar_title_label.pack(anchor="w")

        self.header_subtitle_label = hint_label(
            title_block,
            text=t("tab_monitor"),
        )
        self.header_subtitle_label.pack(anchor="w", pady=(2, 0))

        header_tools = ctk.CTkFrame(header_inner, fg_color="transparent")
        header_tools.pack(side="right")

        language_cluster = header_nav_cluster(header_tools)
        language_cluster.pack(side="right")

        self.language_menu = nav_option_menu(
            language_cluster,
            values=list(LANGUAGE_OPTIONS.keys()),
            command=self._on_language_changed,
        )
        self.language_menu.set(self._language_display_name(self._language))
        self.language_menu.pack(padx=4, pady=4)

        tab_bar_frame = ctk.CTkFrame(root, fg_color="transparent")
        tab_bar_frame.grid(row=1, column=0, sticky="ew", padx=pad, pady=(0, gap))

        self.tab_bar = ctk.CTkSegmentedButton(
            tab_bar_frame,
            values=[self._tab_monitor_label, self._tab_config_label],
            command=self._on_tab_selected,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=BG_INSET,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=BG_INSET,
            unselected_hover_color=HOVER,
            text_color=TEXT_SECONDARY,
            text_color_disabled=TEXT_MUTED,
        )
        self.tab_bar.set(self._tab_monitor_label)
        self.tab_bar.pack(fill="x")

        self.boss_timer_duration_var = ctk.StringVar(
            value=self._format_timer_duration(self.config.monitor.boss_drop_minutes)
        )
        self.common_timer_duration_var = ctk.StringVar(
            value=self._format_timer_duration(self.config.monitor.common_drop_minutes)
        )

        self.content_host = ctk.CTkFrame(root, fg_color="transparent")
        self.content_host.grid(row=2, column=0, sticky="nsew", padx=pad, pady=(0, pad))
        self.content_host.grid_columnconfigure(0, weight=1)
        self.content_host.grid_rowconfigure(0, weight=1)

        self.monitor_tab = ctk.CTkFrame(self.content_host, fg_color="transparent")
        self.config_tab = ctk.CTkFrame(self.content_host, fg_color="transparent")
        for tab in (self.monitor_tab, self.config_tab):
            tab.grid(row=0, column=0, sticky="nsew")
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)

        self._build_monitor_tab(self.monitor_tab, gap=gap, pad=0)
        self._build_config_tab(self.config_tab, gap=gap, pad=0)
        self._show_tab("monitor")

    def _build_config_tab(self, parent, *, gap: int, pad: int) -> None:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_columnconfigure(0, weight=1)

        watch_card = panel_frame(parent)
        watch_card.grid(row=0, column=0, sticky="nsew", pady=(0, gap))
        watch_card.grid_columnconfigure(0, weight=1)
        watch_card.grid_rowconfigure(0, weight=1)

        self.chest_watch_panel = ChestWatchPanel(
            watch_card,
            language=self._language,
            on_change=self._on_watch_changed,
            scroll_max_visible_rows=10,
        )
        self.chest_watch_panel.grid(row=0, column=0, sticky="nsew", padx=PAD_INNER, pady=PAD_INNER)

        settings_card = panel_frame(parent)
        settings_card.grid(row=1, column=0, sticky="ew")
        settings_card.grid_columnconfigure(0, weight=1)

        settings_body = ctk.CTkFrame(settings_card, fg_color="transparent")
        settings_body.grid(row=0, column=0, sticky="ew", padx=PAD_INNER, pady=PAD_INNER)
        settings_body.grid_columnconfigure(0, weight=1)

        settings_row = ctk.CTkFrame(settings_body, fg_color="transparent")
        settings_row.pack(fill="x")

        self.consider_common_var = ctk.BooleanVar(value=self.config.strategy.consider_common_chest)
        self.consider_common_switch = ctk.CTkSwitch(
            settings_row,
            text=t("consider_common_chest"),
            variable=self.consider_common_var,
            command=self._on_watch_changed,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            progress_color=SWITCH_PROGRESS,
            button_color=BG_INSET,
            button_hover_color=BG_INSET,
        )
        self.consider_common_switch.pack(side="left")

        duration_tools = ctk.CTkFrame(settings_row, fg_color="transparent")
        duration_tools.pack(side="right")

        self._build_duration_entry(
            duration_tools,
            self.common_timer_duration_var,
            t("timer_common_duration_minutes"),
            self._on_common_timer_duration_commit,
        )
        self._build_duration_entry(
            duration_tools,
            self.boss_timer_duration_var,
            t("timer_boss_duration_minutes"),
            self._on_boss_timer_duration_commit,
        )

    def _build_monitor_tab(self, parent, *, gap: int, pad: int) -> None:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0, minsize=DROPS_PANEL_WIDTH)

        self.chest_timer_board = ChestTimerBoard(
            parent,
            boss_duration_minutes=self.config.monitor.boss_drop_minutes,
            common_duration_minutes=self.config.monitor.common_drop_minutes,
            show_common_timer=self.config.strategy.consider_common_chest,
            language=self._language,
        )
        self.chest_timer_board.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, gap),
            pady=(0, gap),
        )

        logs_card = panel_frame(parent)
        logs_card.grid(row=0, column=1, rowspan=2, sticky="nsew")
        logs_card.grid_columnconfigure(0, weight=1)
        logs_card.grid_rowconfigure(1, weight=1)

        logs_header = ctk.CTkFrame(logs_card, fg_color="transparent")
        logs_header.grid(row=0, column=0, sticky="ew", padx=PAD_INNER, pady=(PAD_INNER, PAD_SECTION))
        logs_header.grid_columnconfigure(0, weight=1)

        self.events_title_label = section_label(logs_header, text=t("events"))
        self.events_title_label.grid(row=0, column=0, sticky="w")

        self.current_map_label = ctk.CTkLabel(
            logs_header,
            text=t("current_map", label="—"),
            text_color=TEXT_SECONDARY,
            wraplength=DROPS_PANEL_WIDTH - 48,
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            anchor="w",
        )
        self.current_map_label.grid(row=1, column=0, sticky="ew", pady=(PAD_TIGHT, 0))

        log_body = ctk.CTkFrame(logs_card, fg_color="transparent")
        log_body.grid(row=1, column=0, sticky="nsew", padx=PAD_INNER, pady=(0, PAD_INNER))
        log_body.grid_columnconfigure(0, weight=1)
        log_body.grid_rowconfigure(0, weight=1)

        self.log_text = log_textbox(log_body)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")

        monitor_footer = ctk.CTkFrame(parent, fg_color="transparent")
        monitor_footer.grid(row=1, column=0, sticky="ew", padx=(0, gap))
        monitor_footer.grid_columnconfigure(0, weight=1)

        status_row = ctk.CTkFrame(monitor_footer, fg_color="transparent")
        status_row.grid(row=0, column=0, sticky="ew", pady=(0, gap))
        status_row.grid_columnconfigure(0, weight=1)

        self.monitor_status_label = ctk.CTkLabel(
            status_row,
            text=t("status_stopped"),
            text_color=DANGER,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            anchor="w",
        )
        self.monitor_status_label.grid(row=0, column=0, sticky="w")

        self.start_button = primary_button(
            status_row,
            text=t("start_monitor"),
            command=self._toggle_monitor,
            height=36,
        )
        self.start_button.grid(row=0, column=1, sticky="e")

    def _show_tab(self, tab_id: str) -> None:
        self._current_tab = tab_id
        if tab_id == "monitor":
            self.config_tab.grid_remove()
            self.monitor_tab.grid(row=0, column=0, sticky="nsew")
        else:
            self.monitor_tab.grid_remove()
            self.config_tab.grid(row=0, column=0, sticky="nsew")

    def _on_tab_selected(self, value: str) -> None:
        if value == self._tab_monitor_label:
            self._show_tab("monitor")
        else:
            self._show_tab("config")
        self.header_subtitle_label.configure(
            text=t("tab_monitor") if self._current_tab == "monitor" else t("tab_config")
        )

    @staticmethod
    def _language_display_name(language: Language) -> str:
        if language == Language.EN:
            return t("lang_en", language=Language.EN)
        return t("lang_pt_br", language=Language.PT_BR)

    def _on_language_changed(self, display_name: str) -> None:
        language = LANGUAGE_OPTIONS.get(display_name, Language.PT_BR)
        if language == self._language:
            return
        self._language = language
        set_language(language)
        self.config = replace(self.config, language=language)
        save_config(self.config_path, self.config)
        self._apply_language()

    def _apply_language(self) -> None:
        self.title(t("app_title"))
        self.sidebar_title_label.configure(text=t("app_title"))
        self.header_subtitle_label.configure(
            text=t("tab_monitor") if self._current_tab == "monitor" else t("tab_config")
        )
        self.language_menu.set(self._language_display_name(self._language))
        self.consider_common_switch.configure(text=t("consider_common_chest"))
        self.events_title_label.configure(text=t("events"))

        self._tab_monitor_label = t("tab_monitor")
        self._tab_config_label = t("tab_config")
        self.tab_bar.configure(values=[self._tab_monitor_label, self._tab_config_label])
        self.tab_bar.set(
            self._tab_monitor_label if self._current_tab == "monitor" else self._tab_config_label
        )

        monitor_running = self._monitor_thread and self._monitor_thread.is_alive()
        self.start_button.configure(
            text=t("stop_monitor") if monitor_running else t("start_monitor")
        )
        self.monitor_status_label.configure(
            text=t("status_running") if monitor_running else t("status_stopped")
        )

        self.chest_watch_panel.set_language(self._language)
        self.chest_timer_board.set_language(self._language)
        self._refresh_status_labels()

    def _format_timer_duration(self, minutes: float) -> str:
        if minutes == int(minutes):
            return str(int(minutes))
        return f"{minutes:.1f}".rstrip("0").rstrip(".")

    def _parse_timer_duration_value(self, variable: ctk.StringVar) -> float | None:
        raw = variable.get().strip().replace(",", ".")
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        if value < 1 or value > 999:
            return None
        return value

    def _current_boss_drop_minutes(self) -> float:
        parsed = self._parse_timer_duration_value(self.boss_timer_duration_var)
        if parsed is not None:
            return parsed
        return self.config.monitor.boss_drop_minutes

    def _current_common_drop_minutes(self) -> float:
        parsed = self._parse_timer_duration_value(self.common_timer_duration_var)
        if parsed is not None:
            return parsed
        return self.config.monitor.common_drop_minutes

    def _on_boss_timer_duration_commit(self, _event=None) -> None:
        parsed = self._parse_timer_duration_value(self.boss_timer_duration_var)
        if parsed is None:
            self.boss_timer_duration_var.set(
                self._format_timer_duration(self.config.monitor.boss_drop_minutes)
            )
            return

        normalized = self._format_timer_duration(parsed)
        if parsed != self.config.monitor.boss_drop_minutes:
            self.chest_timer_board.set_boss_duration_minutes(parsed)
            self.config = self._collect_config()
            save_config(self.config_path, self.config)
        self.boss_timer_duration_var.set(normalized)

    def _on_common_timer_duration_commit(self, _event=None) -> None:
        parsed = self._parse_timer_duration_value(self.common_timer_duration_var)
        if parsed is None:
            self.common_timer_duration_var.set(
                self._format_timer_duration(self.config.monitor.common_drop_minutes)
            )
            return

        normalized = self._format_timer_duration(parsed)
        if parsed != self.config.monitor.common_drop_minutes:
            self.chest_timer_board.set_common_duration_minutes(parsed)
            self.config = self._collect_config()
            save_config(self.config_path, self.config)
        self.common_timer_duration_var.set(normalized)

    def _load_watch_slots(self) -> None:
        self.chest_watch_panel.load_slots(self.config.chest_farms)

    def _on_watch_changed(self) -> None:
        enabled = self.consider_common_var.get()
        self.chest_timer_board.set_show_common_timer(enabled)
        self._sync_timers()
        if self._monitor_service is not None:
            self._monitor_service.set_consider_common_chest(enabled)
        self.config = self._collect_config()
        save_config(self.config_path, self.config)

    def _sync_timers(self) -> None:
        self.chest_timer_board.set_watch_targets(
            self.chest_watch_panel.collect_slots(),
        )

    def _collect_config(self) -> AppConfig:
        chest_farms = self.chest_watch_panel.collect_slots()
        maps = enabled_farm_maps(chest_farms)
        monitor = replace(
            self.config.monitor,
            boss_drop_minutes=self._current_boss_drop_minutes(),
            common_drop_minutes=self._current_common_drop_minutes(),
        )
        strategy = replace(
            self.config.strategy,
            consider_common_chest=self.consider_common_var.get(),
        )
        width = max(self.winfo_width(), DEFAULT_WINDOW_WIDTH)
        height = max(self.winfo_height(), DEFAULT_WINDOW_HEIGHT)
        return replace(
            self.config,
            monitor=monitor,
            strategy=strategy,
            chest_farms=chest_farms,
            maps=maps,
            language=self._language,
            window_width=width,
            window_height=height,
        )

    def _read_current_stage_key(self) -> int | None:
        try:
            from src.infrastructure.save_reader import SaveReader

            snapshot = SaveReader(
                self.config.save_file_path,
                password=self.config.es3_password,
            ).read_snapshot()
            return snapshot.current_stage_key
        except Exception as error:
            logger.debug("Failed to read current stage from save: %s", error)
            return None

    def _poll_current_stage(self) -> None:
        stage_key = self._read_current_stage_key()
        if stage_key is not None and stage_key != self._current_stage_key:
            self._current_stage_key = stage_key
            self._refresh_status_labels()
        self.after(350, self._poll_current_stage)

    def _refresh_status_labels(self) -> None:
        stage_key = self._current_stage_key
        if stage_key is None:
            stage_key = self._read_current_stage_key()
            if stage_key is not None:
                self._current_stage_key = stage_key

        current_label = (
            format_current_stage_label(stage_key, language=self._language)
            if stage_key is not None
            else None
        )
        self.current_map_label.configure(
            text=t("current_map", label=current_label or "—")
        )

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _handle_confirmed_drop(self, notification: ConfirmedDropNotification) -> None:
        self._confirmed_drop_queue.put(notification)

    def _handle_stage_changed(self, stage_key: int) -> None:
        self._stage_key_queue.put(stage_key)

    def _process_confirmed_drop(self, notification: ConfirmedDropNotification) -> None:
        event = notification.event
        chest_level = notification.chest_level

        self._append_log(notification.log_message)

        if event.chest_type == ChestType.NORMAL_BROWN and not self.consider_common_var.get():
            return

        if event.chest_type == ChestType.NORMAL_BROWN:
            common_key = common_chest_timer_key(chest_level)
            if self.chest_timer_board.has_timer_row(common_key):
                self.chest_timer_board.start_timer(common_key)
            return

        watched = self.chest_watch_panel.watched_levels()
        if chest_level not in watched:
            return

        if not self.chest_timer_board.has_timer_row(chest_level):
            return

        self.chest_timer_board.start_timer(chest_level)

    def _poll_queues(self) -> None:
        try:
            while True:
                try:
                    notification = self._confirmed_drop_queue.get_nowait()
                except queue.Empty:
                    break
                else:
                    self._process_confirmed_drop(notification)

            while True:
                try:
                    message = self._drop_log_queue.get_nowait()
                except queue.Empty:
                    break
                self._append_log(message)

            while True:
                try:
                    stage_key = self._stage_key_queue.get_nowait()
                except queue.Empty:
                    break
                else:
                    if stage_key != self._current_stage_key:
                        self._current_stage_key = stage_key
                        self._refresh_status_labels()
        except Exception:
            logger.exception("Queue polling failed")
        finally:
            self.after(200, self._poll_queues)

    def _tick_timers(self) -> None:
        self.chest_timer_board.tick()
        self.after(250, self._tick_timers)

    def _toggle_monitor(self) -> None:
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitor()
            return
        self._start_monitor()

    def _start_monitor(self) -> None:
        self.config = self._collect_config()
        if not self.config.maps:
            messagebox.showerror("TBH Monitor", t("error_no_maps_start"))
            return

        save_config(self.config_path, self.config)
        set_language(self.config.language)
        self.chest_timer_board.set_boss_duration_minutes(self._current_boss_drop_minutes())
        self.chest_timer_board.set_common_duration_minutes(self._current_common_drop_minutes())
        self.chest_timer_board.set_show_common_timer(self.config.strategy.consider_common_chest)
        self._sync_timers()
        self.chest_timer_board.reset_all()

        enqueue_log = self._drop_log_queue.put
        self._monitor_service = MonitorService(
            self.config,
            dry_run=self.config.monitor.dry_run,
            on_status=enqueue_log,
            on_confirmed_drop=self._handle_confirmed_drop,
            on_drop_log=enqueue_log,
            on_stage_changed=self._handle_stage_changed,
            is_timer_counting=self.chest_timer_board.is_boss_timer_counting,
            is_common_timer_counting=self.chest_timer_board.is_common_timer_counting,
        )

        self._monitor_thread = threading.Thread(target=self._run_monitor_safe, daemon=True)
        self._monitor_thread.start()
        stage_key = self._read_current_stage_key()
        if stage_key is not None:
            self._current_stage_key = stage_key
            self._refresh_status_labels()
        self.start_button.configure(
            text=t("stop_monitor"),
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
        )
        self.monitor_status_label.configure(text=t("status_running"), text_color=SUCCESS)

    def _run_monitor_safe(self) -> None:
        try:
            assert self._monitor_service is not None
            self._monitor_service.run()
        except Exception as error:
            logger.exception("Monitor failed")
            self.after(0, lambda: messagebox.showerror(
                "TBH Monitor",
                t("log_monitor_error", error=error),
            ))

    def _stop_monitor(self) -> None:
        if self._monitor_service is not None:
            self._monitor_service.stop()
        self.start_button.configure(
            text=t("start_monitor"),
            fg_color=BTN_NEUTRAL,
            hover_color=BTN_NEUTRAL_HOVER,
        )
        self.monitor_status_label.configure(text=t("status_stopped"), text_color=DANGER)

    def on_close(self) -> None:
        if self._monitor_service is not None:
            self._monitor_service.stop()
        self.destroy()


def run_gui(config_path: Path) -> None:
    app = MonitorApp(config_path)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
