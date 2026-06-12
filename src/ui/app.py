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
from src.data.chest_catalog import chest_display_label
from src.data.stage_codec import decode_stage_key
from src.data.stage_catalog import find_catalog_entry
from src.domain.chest_level_resolver import drop_chest_level_for_event
from src.domain.chest_event import ChestType
from src.domain.chest_farm import enabled_farm_maps
from src.runtime_paths import app_icon_path
from src.ui.chest_farm_panel import ChestWatchPanel
from src.ui.chest_timer import ChestTimerBoard
from src.ui.i18n import (
    Language,
    chest_kind_label,
    difficulty_display_name,
    format_current_stage_label,
    format_map_drop_label,
    set_language,
    t,
)
from src.ui.theme import (
    BG_INSET,
    BG_ROOT,
    BORDER,
    BTN_NEUTRAL,
    BTN_NEUTRAL_HOVER,
    DANGER,
    DANGER_HOVER,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    GAP_PANEL,
    LEFT_PANEL_MIN_WIDTH,
    PAD_INNER,
    PAD_SECTION,
    PAD_TIGHT,
    PAD_WINDOW,
    SUCCESS,
    SWITCH_PROGRESS,
    TEXT_SECONDARY,
    TIMERS_SECTION_MIN_HEIGHT,
    apply_root_window,
    log_textbox,
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
        self._chest_drop_queue: queue.Queue[tuple[object, int]] = queue.Queue()
        self._stage_key_queue: queue.Queue[int] = queue.Queue()
        self._current_stage_key: int | None = None
        self._window_size_job: str | None = None
        self._ui_ready = False

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

        root.grid_columnconfigure(0, weight=0, minsize=LEFT_PANEL_MIN_WIDTH)
        root.grid_columnconfigure(1, weight=1, minsize=300)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=0, minsize=TIMERS_SECTION_MIN_HEIGHT)

        pad = PAD_WINDOW
        gap = GAP_PANEL

        header = ctk.CTkFrame(root, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=pad, pady=(pad, gap))

        self.sidebar_title_label = section_label(
            header,
            text=t("app_title"),
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        self.sidebar_title_label.pack(side="left")

        header_tools = ctk.CTkFrame(header, fg_color="transparent")
        header_tools.pack(side="right")

        self.language_menu = option_menu(
            header_tools,
            values=list(LANGUAGE_OPTIONS.keys()),
            command=self._on_language_changed,
            width=128,
        )
        self.language_menu.set(self._language_display_name(self._language))
        self.language_menu.pack(side="right", padx=(PAD_TIGHT, 0))

        self.timer_duration_var = ctk.StringVar(
            value=self._format_timer_duration(self.config.monitor.average_drop_minutes)
        )
        self.timer_duration_entry = ctk.CTkEntry(
            header_tools,
            textvariable=self.timer_duration_var,
            width=48,
            height=28,
            justify="center",
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
            fg_color=BG_INSET,
        )
        self.timer_duration_entry.pack(side="right", padx=(PAD_TIGHT, 0))
        self.timer_duration_entry.bind("<Return>", self._on_timer_duration_commit)
        self.timer_duration_entry.bind("<FocusOut>", self._on_timer_duration_commit)

        self.timer_duration_label = ctk.CTkLabel(
            header_tools,
            text=t("timer_duration_minutes"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
        )
        self.timer_duration_label.pack(side="right", padx=(PAD_TIGHT, 0))

        self.consider_common_var = ctk.BooleanVar(value=self.config.strategy.consider_common_chest)
        self.consider_common_switch = ctk.CTkSwitch(
            header_tools,
            text=t("consider_common_chest"),
            variable=self.consider_common_var,
            command=self._on_watch_changed,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            progress_color=SWITCH_PROGRESS,
            button_color=BG_INSET,
            button_hover_color=BG_INSET,
        )
        self.consider_common_switch.pack(side="right", padx=(PAD_TIGHT, 0))

        left_card = panel_frame(root)
        left_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(pad, gap),
            pady=(0, gap),
        )
        left_card.grid_columnconfigure(0, weight=1)
        left_card.grid_rowconfigure(0, weight=1)
        left_card.grid_rowconfigure(1, weight=0)

        self.chest_watch_panel = ChestWatchPanel(
            left_card,
            language=self._language,
            on_change=self._on_watch_changed,
        )
        self.chest_watch_panel.grid(row=0, column=0, sticky="nsew", padx=PAD_INNER, pady=PAD_INNER)

        self.start_button = primary_button(
            left_card,
            text=t("start_monitor"),
            command=self._toggle_monitor,
        )
        self.start_button.grid(row=1, column=0, sticky="ew", padx=PAD_INNER, pady=(0, PAD_INNER))

        logs_card = panel_frame(root)
        logs_card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(0, pad),
            pady=(0, gap),
        )
        logs_card.grid_columnconfigure(0, weight=1)
        logs_card.grid_rowconfigure(1, weight=1)

        logs_header = ctk.CTkFrame(logs_card, fg_color="transparent")
        logs_header.grid(row=0, column=0, sticky="ew", padx=PAD_INNER, pady=(PAD_INNER, PAD_SECTION))

        self.events_title_label = section_label(logs_header, text=t("events"))
        self.events_title_label.pack(side="left")

        self.current_map_label = ctk.CTkLabel(
            logs_header,
            text=t("current_map", label="—"),
            text_color=TEXT_SECONDARY,
            wraplength=300,
            justify="right",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            anchor="e",
        )
        self.current_map_label.pack(side="right")

        log_body = ctk.CTkFrame(logs_card, fg_color="transparent")
        log_body.grid(row=1, column=0, sticky="nsew", padx=PAD_INNER, pady=(0, PAD_INNER))
        log_body.grid_columnconfigure(0, weight=1)
        log_body.grid_rowconfigure(0, weight=1)

        self.log_text = log_textbox(log_body)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")

        status_footer = ctk.CTkFrame(logs_card, fg_color="transparent")
        status_footer.grid(row=2, column=0, sticky="ew", padx=PAD_INNER, pady=(0, PAD_INNER))

        self.monitor_status_label = ctk.CTkLabel(
            status_footer,
            text=t("status_stopped"),
            text_color=DANGER,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            anchor="w",
        )
        self.monitor_status_label.pack(side="left")

        self.chest_timer_board = ChestTimerBoard(
            root,
            duration_minutes=self.config.monitor.average_drop_minutes,
            language=self._language,
        )
        self.chest_timer_board.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=pad,
            pady=(0, pad),
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
        self.language_menu.set(self._language_display_name(self._language))
        self.consider_common_switch.configure(text=t("consider_common_chest"))
        self.timer_duration_label.configure(text=t("timer_duration_minutes"))
        self.events_title_label.configure(text=t("events"))

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

    def _parse_timer_duration_value(self) -> float | None:
        raw = self.timer_duration_var.get().strip().replace(",", ".")
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        if value < 1 or value > 999:
            return None
        return value

    def _current_timer_duration_minutes(self) -> float:
        parsed = self._parse_timer_duration_value()
        if parsed is not None:
            return parsed
        return self.config.monitor.average_drop_minutes

    def _on_timer_duration_commit(self, _event=None) -> None:
        parsed = self._parse_timer_duration_value()
        if parsed is None:
            self.timer_duration_var.set(
                self._format_timer_duration(self.config.monitor.average_drop_minutes)
            )
            return

        normalized = self._format_timer_duration(parsed)
        if parsed == self.config.monitor.average_drop_minutes:
            self.timer_duration_var.set(normalized)
            return

        self.chest_timer_board.set_duration_minutes(parsed)
        self.config = self._collect_config()
        save_config(self.config_path, self.config)
        self.timer_duration_var.set(normalized)

    def _load_watch_slots(self) -> None:
        self.chest_watch_panel.load_slots(self.config.chest_farms)

    def _on_watch_changed(self) -> None:
        enabled = self.consider_common_var.get()
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
            average_drop_minutes=self._current_timer_duration_minutes(),
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

    def _map_label_for_stage_key(self, stage_key: int) -> str:
        entry = find_catalog_entry(stage_key)
        stage = decode_stage_key(stage_key)
        map_name = entry.name if entry is not None else stage.label
        boss_drop_percent = entry.boss_chest_drop_percent if entry is not None else None
        return format_map_drop_label(
            act=stage.act,
            stage=stage.stage,
            map_name=map_name,
            boss_drop_percent=boss_drop_percent,
            language=self._language,
        )

    def _handle_chest_drop(self, event, stage_key: int) -> None:
        self._chest_drop_queue.put((event, stage_key))

    def _handle_stage_changed(self, stage_key: int) -> None:
        self._stage_key_queue.put(stage_key)

    def _process_chest_drop_ui(self, event, stage_key: int) -> None:
        from datetime import datetime

        if event.chest_type == ChestType.NORMAL_BROWN and not self.consider_common_var.get():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        map_label = self._map_label_for_stage_key(stage_key)
        level = drop_chest_level_for_event(event, stage_key)
        if level is None:
            return

        watched = self.chest_watch_panel.watched_levels()
        if level not in watched:
            self._append_log(
                t(
                    "log_timer_not_watched",
                    language=self._language,
                    time=timestamp,
                    level=level,
                    map_name=map_label,
                )
            )
            return

        if self.chest_timer_board.start_timer_on_drop(level):
            return

        timer_label = chest_display_label(level, language=self._language, short=True)
        if event.chest_type == ChestType.NORMAL_BROWN:
            timer_label = (
                f"{chest_kind_label(ChestType.NORMAL_BROWN, language=self._language)} · "
                f"{timer_label}"
            )

        self._append_log(
            t(
                "log_timer_skipped",
                language=self._language,
                time=timestamp,
                label=timer_label,
            )
        )

    def _poll_queues(self) -> None:
        while True:
            try:
                event, stage_key = self._chest_drop_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self._process_chest_drop_ui(event, stage_key)

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
        self.chest_timer_board.set_duration_minutes(self._current_timer_duration_minutes())
        self._sync_timers()
        self.chest_timer_board.reset_all()

        self._monitor_service = MonitorService(
            self.config,
            dry_run=self.config.monitor.dry_run,
            on_chest_drop=self._handle_chest_drop,
            on_drop_log=lambda message: self._drop_log_queue.put(message),
            on_stage_changed=self._handle_stage_changed,
            is_timer_counting=self.chest_timer_board.is_timer_counting,
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
