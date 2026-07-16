"""Legacy clipping plane wrappers."""

from __future__ import annotations

from typing import Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import glClipPlane

from picogl.backend.gl.enums.legacy import GLLegacyClipPlane


def gl_clip_plane(plane: GLLegacyClipPlane, equation: Sequence[float]) -> None:
    """Define a clipping plane equation (a, b, c, d)."""
    glClipPlane(int(plane), equation)
