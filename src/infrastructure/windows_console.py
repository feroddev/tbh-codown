"""Windows console helpers for PyInstaller builds."""

from __future__ import annotations

import os
import sys


def ensure_console_for_cli() -> None:
    """Attach or create a console when running CLI subcommands from a windowed exe."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return

    import ctypes

    kernel32 = ctypes.windll.kernel32
    if kernel32.GetConsoleWindow():
        return

    attached_to_parent = bool(kernel32.AttachConsole(ctypes.c_ulong(-1).value))
    if not attached_to_parent and not kernel32.AllocConsole():
        return

    _reopen_standard_streams()


def _reopen_standard_streams() -> None:
    import msvcrt

    try:
        sys.stdout = os.fdopen(
            msvcrt.get_osfhandle(1), "w", encoding="utf-8", errors="replace", closefd=False
        )
        sys.stderr = os.fdopen(
            msvcrt.get_osfhandle(2), "w", encoding="utf-8", errors="replace", closefd=False
        )
        sys.stdin = os.fdopen(
            msvcrt.get_osfhandle(0), "r", encoding="utf-8", errors="replace", closefd=False
        )
    except OSError:
        sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        sys.stdin = open("CONIN$", "r", encoding="utf-8", errors="replace")

