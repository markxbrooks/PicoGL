"""Prefer Apple GLUT.framework over Homebrew freeglut on macOS.

Homebrew freeglut installs ``libglut.dylib`` (X11 + Mesa). On case-insensitive
APFS, ``ctypes.util.find_library("GLUT")`` resolves that to
``/opt/homebrew/lib/libGLUT.dylib``, so PyOpenGL's Darwin platform loads
freeglut instead of ``/System/Library/Frameworks/GLUT.framework``.

freeglut then creates an X11 window with no CGL context, and PyOpenGL raises:
``Attempt to retrieve context when no valid context`` on ``glutDisplayFunc``.

Import this module **before** ``import OpenGL.GLUT``.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys

_APPLE_GL = "/System/Library/Frameworks/OpenGL.framework/OpenGL"
_APPLE_GLUT = "/System/Library/Frameworks/GLUT.framework/GLUT"
_patched = False


def prefer_apple_glut() -> bool:
    """Make PyOpenGL bind Cocoa GLUT instead of Homebrew freeglut."""
    global _patched
    if sys.platform != "darwin" or _patched:
        return _patched
    try:
        ctypes.CDLL(_APPLE_GL, mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(_APPLE_GLUT, mode=ctypes.RTLD_GLOBAL)
    except OSError:
        return False

    original_find = ctypes.util.find_library

    def find_library(name: str):
        if name in ("GLUT", "glut"):
            return _APPLE_GLUT
        if name == "OpenGL":
            return _APPLE_GL
        return original_find(name)

    ctypes.util.find_library = find_library  # type: ignore[assignment]
    _patched = True
    return True


prefer_apple_glut()
