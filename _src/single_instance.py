"""Ensure only one EVE Settings Copy UI instance is running."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

MUTEX_NAME = "Local\\EveSettingsCopy_SingleInstance_HesBi"
WINDOW_TITLE_PREFIX = "EVE Settings Copy"

_mutex_handle = None  # keep alive for process lifetime


def _user32():
    return ctypes.windll.user32


def find_app_hwnd() -> int:
    """Find the main (or splash) window by title prefix."""
    user32 = _user32()
    found = ctypes.c_void_p()

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, _lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value or ""
        if title.startswith(WINDOW_TITLE_PREFIX):
            found.value = hwnd
            return False
        return True

    user32.EnumWindows(enum_proc, 0)
    return int(found.value or 0)


def activate_existing_window() -> bool:
    """Bring an existing app window to the foreground. Returns True if found."""
    if sys.platform != "win32":
        return False
    user32 = _user32()
    hwnd = find_app_hwnd()
    if not hwnd:
        return False

    SW_RESTORE = 9
    SW_SHOW = 5
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    else:
        user32.ShowWindow(hwnd, SW_SHOW)

    foreground = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    cur_tid = user32.GetWindowThreadProcessId(foreground, ctypes.byref(pid))
    tgt_tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if cur_tid != tgt_tid:
        user32.AttachThreadInput(cur_tid, tgt_tid, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    if cur_tid != tgt_tid:
        user32.AttachThreadInput(cur_tid, tgt_tid, False)
    return True


def already_running() -> bool:
    """True if another instance owns the single-instance mutex."""
    if sys.platform != "win32":
        return False
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenMutexW(0x00100000, False, MUTEX_NAME)  # SYNCHRONIZE
    if handle:
        kernel32.CloseHandle(handle)
        return True
    return False


def try_become_primary() -> bool:
    """
    Claim the single-instance mutex.
    Returns True if this process is primary; False if another instance was activated.
    """
    global _mutex_handle
    if sys.platform != "win32":
        return True

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    already = kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
    if already:
        if handle:
            kernel32.CloseHandle(handle)
        activate_existing_window()
        return False

    _mutex_handle = handle
    return True
