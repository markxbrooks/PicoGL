"""
gl polygon mode context manager
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from backend.gl.backend import GLBackend
from backend.gl.state.fill import GLFillMode, GLFace


@contextmanager
def gl_polygon_mode_context(gl_backend: GLBackend, mode: GLFillMode) -> Iterator[None]:
    """Temporarily set polygon mode and restore fill on exit."""
    gl_backend.raster.set_polygon_mode(GLFace.FRONT_AND_BACK, mode)
    try:
        yield
    finally:
        gl_backend.raster.set_polygon_mode(GLFace.FRONT_AND_BACK, GLFillMode.FILL)
