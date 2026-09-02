import ctypes
import os
import subprocess
import sys
from contextlib import contextmanager
from ctypes import wintypes
from threading import Event

import gmsh
import keyboard

if not gmsh.isInitialized():
    gmsh.initialize(interruptible=False)

gonelab = gmsh.onelab
goption = gmsh.option
_selection_in_progress = Event()

if os.name == "nt":
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _user32.GetForegroundWindow.restype = wintypes.HWND
    _user32.GetWindowThreadProcessId.argtypes = (
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    )
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD


def is_gmsh_focused():
    """Return whether the foreground window belongs to this Gmsh process."""
    if os.name == "nt":
        foreground_window = _user32.GetForegroundWindow()
        if not foreground_window:
            return False

        foreground_process_id = wintypes.DWORD()
        _user32.GetWindowThreadProcessId(
            foreground_window, ctypes.byref(foreground_process_id)
        )
        return foreground_process_id.value == os.getpid()

    if sys.platform.startswith("linux"):
        if os.environ.get(
            "XDG_SESSION_TYPE", ""
        ).lower() == "wayland" or os.environ.get("WAYLAND_DISPLAY"):
            return False

        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowpid"],
                check=True,
                capture_output=True,
                text=True,
                timeout=1,
            )
            output_lines = result.stdout.splitlines()
            return bool(output_lines) and int(output_lines[-1]) == os.getpid()
        except (OSError, subprocess.SubprocessError, ValueError):
            return False

    return True


def is_selection_in_progress():
    """Return whether an interactive Gmsh entity selection is active."""
    return _selection_in_progress.is_set()


@contextmanager
def selecting_entities():
    """Mark the duration of an interactive Gmsh entity selection."""
    _selection_in_progress.set()
    try:
        yield
    finally:
        _selection_in_progress.clear()


def _add_hotkey(hotkey, callback):
    """Register a hotkey that only runs while the Gmsh window is focused."""

    def callback_if_focused():
        if is_gmsh_focused() and not is_selection_in_progress():
            callback()

    return keyboard.add_hotkey(hotkey, callback_if_focused)


def toggleSurfaceTypeCommand():
    """Toggle surface rendering type between cross (0) and solid (2)."""
    current_type = int(goption.getNumber("Geometry.SurfaceType"))
    new_type = 0 if current_type == 2 else 2
    goption.setNumber("Geometry.SurfaceType", new_type)
    print(f"Info    : Geometry.SurfaceType set to {new_type}")
    return True


_add_hotkey(
    "ctrl+z",
    lambda: (
        gonelab.setNumber("Geometry/Undo previous action", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "h",
    lambda: (
        gonelab.setNumber("Geometry/Heal/ CAD", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "shift+h",
    lambda: (
        gonelab.setNumber("Geometry/Heal/ Surfaces", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "p",
    lambda: (
        gonelab.setNumber("Geometry/Project/A point on a curve", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "s",
    lambda: (
        gonelab.setNumber("Geometry/Project/A surface on a surface", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "l",
    lambda: (
        gonelab.setNumber("Geometry/Split/A volume by a point loop", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "u",
    lambda: (
        gonelab.setNumber("Geometry/Split/A triangle surface", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "i",
    lambda: (
        gonelab.setNumber("Geometry/Split/A wedge volume", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "m",
    lambda: (
        gonelab.setNumber(
            "Geometry/Split/A volume by an infinite plane (3 points)", [1]
        ),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "k",
    lambda: (
        gonelab.setNumber("Geometry/Split/A volume by a finite plane (4 points)", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "r",
    lambda: (
        gonelab.setNumber("Geometry/Remove/Surfaces", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "t",
    lambda: (
        gonelab.setNumber("Geometry/Remove/Curves", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "shift+t",
    lambda: (
        gonelab.setNumber("Geometry/Remove/All orphan curves", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "shift+r",
    lambda: (
        gonelab.setNumber("Geometry/Remove/All duplicates", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "c",
    lambda: (
        gonelab.setNumber("Geometry/Merge/Two Curves", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "v",
    lambda: (
        gonelab.setNumber("Geometry/Merge/Two Surfaces", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "z",
    lambda: (
        gonelab.setNumber("Geometry/Add/A surface by curve loop", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "e",
    lambda: (
        gonelab.setNumber("Geometry/Add/A surface by point loop", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "d",
    lambda: (
        gonelab.setNumber("Geometry/Add/A volume between two surfaces", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "x",
    lambda: (
        gonelab.setNumber("Geometry/Add/A point on a curve (ratio)", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "y",
    lambda: (
        gonelab.setNumber("Geometry/Split/A surface by a curve", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)
_add_hotkey(
    "n",
    lambda: (
        gonelab.setNumber("Mesh/Set number of nodes on /One edge", [1]),
        gonelab.setString("ONELAB/Action", ["check"]),
    ),
)


_add_hotkey("alt+t", toggleSurfaceTypeCommand)
