"""
Glut display and input callback registration.
"""

from __future__ import annotations

from typing import Callable

from OpenGL.GLUT import (glutDisplayFunc, glutIdleFunc, glutKeyboardFunc,
                         glutMotionFunc, glutMouseFunc, glutPostRedisplay,
                         glutReshapeFunc)

# Before OpenGL.GLUT: prefer Apple GLUT (macOS) / GLX (Linux+Wayland).
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401

DisplayCallback = Callable[[], None]
IdleCallback = Callable[[], None]
ReshapeCallback = Callable[[int, int], None]
KeyboardCallback = Callable[[bytes, int, int], None]
MouseCallback = Callable[[int, int, int, int], None]
MotionCallback = Callable[[int, int], None]


def glut_post_redisplay() -> None:
    """Request a redraw of the current window."""
    glutPostRedisplay()


def glut_display_func(func: DisplayCallback) -> None:
    """Register the display (redraw) callback."""
    glutDisplayFunc(func)


def glut_reshape_func(func: ReshapeCallback) -> None:
    """Register the window reshape callback."""
    glutReshapeFunc(func)


def glut_keyboard_func(func: KeyboardCallback) -> None:
    """Register the ASCII keyboard callback."""
    glutKeyboardFunc(func)


def glut_mouse_func(func: MouseCallback) -> None:
    """Register the mouse button callback."""
    glutMouseFunc(func)


def glut_motion_func(func: MotionCallback) -> None:
    """Register the mouse motion (drag) callback."""
    glutMotionFunc(func)


def glut_idle_func(func: IdleCallback | None) -> None:
    """Register the idle callback, or ``None`` to clear it."""
    glutIdleFunc(func)
