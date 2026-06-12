from __future__ import annotations

import customtkinter as ctk

# Backgrounds (gray theme)
BG_ROOT = "#3a3a3a"
BG_SURFACE = "#454545"
BG_ELEVATED = "#505050"
BG_INSET = "#3f3f3f"

# Borders & accents
BORDER = "#5a5a5a"
BORDER_SUBTLE = "#4a4a4a"
BORDER_FOCUS = "#737373"
HOVER = "#5c5c5c"
HOVER_STRONG = "#666666"
ACCENT = "#505050"
ACCENT_HOVER = "#5c5c5c"
BTN_NEUTRAL = "#505050"
BTN_NEUTRAL_HOVER = "#5c5c5c"

# Text
TEXT_PRIMARY = "#f5f5f5"
TEXT_SECONDARY = "#c4c4c4"
TEXT_MUTED = "#9ca3af"

# Status
SUCCESS = "#4ade80"
DANGER = "#ef4444"
DANGER_HOVER = "#dc2626"
WARNING = "#fbbf24"
TIMER_ACTIVE = "#22d3ee"
TIMER_WAITING = "#67e8f9"
NEXT_TARGET_BORDER = "#4ade80"
SWITCH_PROGRESS = "#22d3ee"

# Layout
RADIUS_PANEL = 14
RADIUS_CARD = 12
RADIUS_CONTROL = 10
RADIUS_SMALL = 8

PAD_WINDOW = 20
PAD_SECTION = 12
PAD_INNER = 14
PAD_TIGHT = 8
GAP_PANEL = 12

DEFAULT_WINDOW_WIDTH = 940
DEFAULT_WINDOW_HEIGHT = 700
TIMERS_SECTION_MIN_HEIGHT = 188
LEFT_PANEL_MIN_WIDTH = 458
DROPS_PANEL_WIDTH = 300
LOG_FONT_SIZE = 12

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 20, "bold")


def apply_root_window(window: ctk.CTk) -> None:
    window.configure(fg_color=BG_ROOT)


def panel_frame(master, **kwargs) -> ctk.CTkFrame:
    defaults = {
        "fg_color": BG_SURFACE,
        "corner_radius": RADIUS_PANEL,
        "border_width": 1,
        "border_color": BORDER_SUBTLE,
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)


def inset_frame(master, **kwargs) -> ctk.CTkFrame:
    defaults = {
        "fg_color": BG_INSET,
        "corner_radius": RADIUS_CARD,
        "border_width": 1,
        "border_color": BORDER_SUBTLE,
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)


def section_label(master, text: str, **kwargs) -> ctk.CTkLabel:
    defaults = {
        "text": text,
        "font": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        "text_color": TEXT_PRIMARY,
        "anchor": "w",
    }
    defaults.update(kwargs)
    return ctk.CTkLabel(master, **defaults)


def hint_label(master, text: str, **kwargs) -> ctk.CTkLabel:
    defaults = {
        "text": text,
        "font": ctk.CTkFont(family="Segoe UI", size=11),
        "text_color": TEXT_MUTED,
        "anchor": "w",
    }
    defaults.update(kwargs)
    return ctk.CTkLabel(master, **defaults)


def primary_button(master, **kwargs) -> ctk.CTkButton:
    defaults = {
        "height": 40,
        "corner_radius": RADIUS_CONTROL,
        "font": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        "fg_color": BTN_NEUTRAL,
        "hover_color": BTN_NEUTRAL_HOVER,
        "border_width": 1,
        "border_color": BORDER,
    }
    defaults.update(kwargs)
    return ctk.CTkButton(master, **defaults)


def secondary_button(master, **kwargs) -> ctk.CTkButton:
    defaults = {
        "height": 34,
        "corner_radius": RADIUS_CONTROL,
        "font": ctk.CTkFont(family="Segoe UI", size=12),
        "fg_color": BG_ELEVATED,
        "hover_color": HOVER,
        "border_width": 1,
        "border_color": BORDER,
    }
    defaults.update(kwargs)
    return ctk.CTkButton(master, **defaults)


def option_menu(master, **kwargs) -> ctk.CTkOptionMenu:
    defaults = {
        "height": 32,
        "corner_radius": RADIUS_SMALL,
        "font": ctk.CTkFont(family="Segoe UI", size=12),
        "fg_color": BG_ELEVATED,
        "button_color": BG_INSET,
        "button_hover_color": HOVER,
        "dropdown_fg_color": BG_SURFACE,
        "dropdown_hover_color": HOVER,
        "dropdown_text_color": TEXT_PRIMARY,
    }
    defaults.update(kwargs)
    return ctk.CTkOptionMenu(master, **defaults)


def log_textbox(master, **kwargs) -> ctk.CTkTextbox:
    defaults = {
        "corner_radius": RADIUS_CARD,
        "border_width": 1,
        "border_color": BORDER_SUBTLE,
        "fg_color": BG_INSET,
        "font": ctk.CTkFont(family="Segoe UI", size=LOG_FONT_SIZE),
        "wrap": "word",
    }
    defaults.update(kwargs)
    return ctk.CTkTextbox(master, **defaults)
