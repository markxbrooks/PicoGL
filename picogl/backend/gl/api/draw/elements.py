from __future__ import annotations

from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawElements

from picogl.backend.gl.api.draw.helper import draw_pointer, gl_enum
from picogl.backend.gl.enums import GLIndexType, GLDrawMode


def gl_draw_elements(
    index_count: int,
    dtype: int | None = GLIndexType.UNSIGNED_INT,
    mode: GLDrawMode | int | None = GLDrawMode.TRIANGLES,
    pointer: Any | None = None,
    offset: int = 0,
) -> None:
    """
    Issue ``glDrawElements``.

    *pointer* may be a client index array, ``None`` (EBO bound), or omitted to use *offset*.
    """
    assert dtype is not None
    assert mode is not None
    pointer = draw_pointer(pointer, offset)
    glDrawElements(
        gl_enum(mode),
        int(index_count),
        gl_enum(dtype),
        pointer,
    )
