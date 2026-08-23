"""GLUT initialization helpers."""

from __future__ import annotations

import sys
from typing import Sequence

from OpenGL.GLUT import (glutCreateWindow, glutInit, glutInitDisplayMode,
                         glutInitWindowSize, glutMainLoop)

# Before OpenGL.GLUT: prefer Apple GLUT (macOS) / GLX (Linux+Wayland).
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.backend.glut.enums import GLUTDisplayMode


def glut_init(argv: Sequence[str] | None = None) -> None:
    """Initialize GLUT.

    :param argv: Program arguments; defaults to ``sys.argv``.
    """
    glutInit(list(sys.argv if argv is None else argv))


def glut_init_display_mode(mode: GLUTDisplayMode | int) -> None:
    """Set the initial display mode (e.g. RGBA | DOUBLE | DEPTH)."""
    glutInitDisplayMode(int(mode))


def glut_init_window_size(width: int, height: int) -> None:
    """Set the initial window size in pixels."""
    glutInitWindowSize(int(width), int(height))


def glut_create_window(title: str | bytes) -> int:
    """Create a GLUT window and return its window id.

    String titles are encoded as UTF-8.
    """
    title_bytes = title.encode("utf-8") if isinstance(title, str) else title
    return int(glutCreateWindow(title_bytes))


def glut_main_loop() -> None:
    """Enter the GLUT event processing loop (does not return)."""
    glutMainLoop()
