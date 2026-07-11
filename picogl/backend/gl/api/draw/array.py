from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays

from picogl.backend.gl.api.draw.helper import gl_enum
from picogl.backend.gl.enums import GLDrawMode


def gl_draw_arrays(
    index_count: int,
    mode: GLDrawMode | int,
    first: int = 0,
) -> None:
    """Issue ``glDrawArrays`` with PicoGL draw-mode enums or raw gl constants."""
    assert mode is not None
    glDrawArrays(gl_enum(mode), int(first), int(index_count))
