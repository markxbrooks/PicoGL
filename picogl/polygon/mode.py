"""
gl polygon mode context manager
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POLYGON_MODE
from picogl.backend.gl.api.get_integerv import gl_get_integerv
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLFillMode
from picogl.core.polygon.mode import gl_polygon_mode as _set_polygon_mode


@contextmanager
def gl_polygon_mode_context(mode: GLFillMode) -> Iterator[None]:
    """Temporarily set polygon mode and restore the previous front/back modes on exit."""
    prev_mode = gl_get_integerv(GL_POLYGON_MODE)
    prev_front_mode, prev_back_mode = prev_mode[0], prev_mode[1]
    _set_polygon_mode(GLMaterialFace.FRONT_AND_BACK, mode)
    try:
        yield
    finally:
        _set_polygon_mode(GLMaterialFace.FRONT, prev_front_mode)
        _set_polygon_mode(GLMaterialFace.BACK, prev_back_mode)


# Backward-compatible alias used as ``with gl_polygon_mode(mode):``.
gl_polygon_mode = gl_polygon_mode_context
