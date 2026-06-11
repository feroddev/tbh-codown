from __future__ import annotations

import logging
import time

import win32api
import win32con
import win32gui
import win32process

logger = logging.getLogger(__name__)


def find_window_handle(title_fragment: str) -> int | None:
    matches: list[int] = []

    def callback(hwnd: int, _: object) -> bool:
        if not win32gui.IsWindow(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if title and title_fragment.lower() in title.lower():
            if win32gui.IsIconic(hwnd) or win32gui.IsWindowVisible(hwnd):
                matches.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    if not matches:
        return None

    for hwnd in matches:
        if win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd):
            return hwnd
    return matches[0]


def get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return left, top, right - left, bottom - top


def focus_window(hwnd: int) -> None:
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.15)

    foreground = win32gui.GetForegroundWindow()
    if foreground == hwnd:
        return

    foreground_thread = win32process.GetWindowThreadProcessId(foreground)[0]
    target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
    current_thread = win32api.GetCurrentThreadId()

    attached_to_foreground = False
    attached_to_target = False
    try:
        if foreground_thread and foreground_thread != current_thread:
            win32process.AttachThreadInput(current_thread, foreground_thread, True)
            attached_to_foreground = True
        if target_thread and target_thread != current_thread:
            win32process.AttachThreadInput(current_thread, target_thread, True)
            attached_to_target = True

        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
    finally:
        if attached_to_target:
            win32process.AttachThreadInput(current_thread, target_thread, False)
        if attached_to_foreground:
            win32process.AttachThreadInput(current_thread, foreground_thread, False)

    time.sleep(0.2)


def focus_game_window(title_fragment: str) -> tuple[int, int, int, int]:
    hwnd = find_window_handle(title_fragment)
    if hwnd is None:
        raise RuntimeError(f"Janela '{title_fragment}' não encontrada")
    focus_window(hwnd)
    return get_window_rect(hwnd)
