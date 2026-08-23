"""Convenience: bind an element buffer and draw ushort triangles."""

from __future__ import annotations

from picogl.backend.gl.api.buffer.bind import gl_bind_buffer
from picogl.backend.gl.api.draw.elements import gl_draw_elements
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode, GLNumeric


def gl_bind_elements(index_buffer, size: int) -> None:
    """Bind ELEMENT buffer and draw triangles (ushort indices)."""
    gl_bind_buffer(GLBufferTarget.ELEMENT, index_buffer)
    # PicoGL: (index_count, dtype, mode) — not raw GL (mode, count, type).
    gl_draw_elements(size, GLNumeric.UNSIGNED_SHORT, GLDrawMode.TRIANGLES)
