"""Legacy attribute stack wrappers."""

from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_0 import glPopAttrib, glPushAttrib
from picogl.backend.gl.enums.bitmask import GLBitMask


def gl_push_attrib(mask: GLBitMask | int) -> None:
    """Push server attribute bits onto the attribute stack."""
    glPushAttrib(int(mask))


def gl_pop_attrib() -> None:
    """Pop server attribute bits from the attribute stack."""
    glPopAttrib()
