"""
gl polygon mode context manager
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from picogl.backend.gl.state.fill import GLFace, GLFillMode
from picogl.core.polygon.mode import gl_polygon_mode


@contextmanager
def gl_polygon_mode_context(mode: GLFillMode) -> Iterator[None]:
    """Temporarily set polygon mode and restore fill on exit."""
    gl_polygon_mode(GLFace.FRONT_AND_BACK, mode)
    try:
        yield
    finally:
        gl_polygon_mode(GLFace.FRONT_AND_BACK, GLFillMode.FILL)
