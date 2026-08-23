"""Prefer GLX over EGL for PyOpenGL on Linux.

Under Wayland, PyOpenGL often selects the EGL platform. freeglut still creates
GLX contexts, so ``GetCurrentContext()`` returns 0 and ``glutDisplayFunc`` raises:

    Attempt to retrieve context when no valid context

Set ``PYOPENGL_PLATFORM=glx`` **before** importing OpenGL.

Import this module before ``import OpenGL`` / ``OpenGL.GLUT``.
"""

from __future__ import annotations

import os
import sys

_patched = False


def prefer_glx() -> bool:
    """Force PyOpenGL onto the GLX platform on Linux when unset."""
    global _patched
    if not sys.platform.startswith("linux"):
        return False
    if _patched:
        return os.environ.get("PYOPENGL_PLATFORM") == "glx"

    current = os.environ.get("PYOPENGL_PLATFORM")
    if current:
        _patched = current == "glx"
        return _patched

    os.environ["PYOPENGL_PLATFORM"] = "glx"
    _patched = True
    return True


prefer_glx()
