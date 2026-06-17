from __future__ import annotations

import customtkinter as ctk

# Backgrounds — premium dark palette
BG_ROOT = "#0B0F19"
BG_SURFACE = "#111827"
BG_ELEVATED = "#151B2D"
BG_INSET = "#0D1220"

# Borders & accents
BORDER = "#1F2937"
BORDER_SUBTLE = "#1A2234"
BORDER_FOCUS = "#8B5CF6"
HOVER = "#1E293B"
HOVER_STRONG = "#253045"
ACCENT = "#8B5CF6"
ACCENT_HOVER = "#A78BFA"
BTN_NEUTRAL = "#8B5CF6"
BTN_NEUTRAL_HOVER = "#A78BFA"

# Text
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"

# Status
SUCCESS = "#14B8A6"
DANGER = "#F87171"
DANGER_HOVER = "#EF4444"
WARNING = "#FBBF24"
TIMER_ACTIVE = "#8B5CF6"
TIMER_WAITING = "#A78BFA"
COMMON_TIMER_ACTIVE = "#14B8A6"
NEXT_TARGET_BORDER = "#14B8A6"
SWITCH_PROGRESS = "#8B5CF6"

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
DEFAULT_WINDOW_HEIGHT = 720
TIMERS_SECTION_MIN_HEIGHT = 240
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
        "border_width": 0,
        "text_color": TEXT_PRIMARY,
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
        "text_color": TEXT_SECONDARY,
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
        "text_color": TEXT_SECONDARY,
    }
    defaults.update(kwargs)
    return ctk.CTkOptionMenu(master, **defaults)


def header_nav_cluster(master, **kwargs) -> ctk.CTkFrame:
    """Compact header control cluster matching web `.tbh-nav`."""
    defaults = {
        "fg_color": BG_ELEVATED,
        "corner_radius": RADIUS_SMALL,
        "border_width": 1,
        "border_color": BORDER_SUBTLE,
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(master, **defaults)


def nav_option_menu(master, **kwargs) -> ctk.CTkOptionMenu:
    """Inline language/menu control for header nav clusters."""
    defaults = {
        "height": 30,
        "width": 132,
        "corner_radius": RADIUS_SMALL - 2,
        "font": ctk.CTkFont(family="Segoe UI", size=12),
        "fg_color": BG_ELEVATED,
        "button_color": BG_ELEVATED,
        "button_hover_color": HOVER,
        "dropdown_fg_color": BG_SURFACE,
        "dropdown_hover_color": HOVER,
        "dropdown_text_color": TEXT_PRIMARY,
        "text_color": TEXT_SECONDARY,
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
        "text_color": TEXT_MUTED,
        "wrap": "word",
    }
    defaults.update(kwargs)
    return ctk.CTkTextbox(master, **defaults)
