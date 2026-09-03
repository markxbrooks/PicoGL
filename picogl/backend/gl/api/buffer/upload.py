"""Typed helpers for uploading CPU arrays into the currently bound GL buffer."""

from __future__ import annotations

from OpenGL.GL import GLfloat, GLushort

from picogl.backend.gl.api.buffer.data import gl_buffer_data
from picogl.backend.gl.enums import GLBufferTarget, GLUsageHint


def gl_upload_float_buffer(
    data: list[float],
    buffer_target: GLBufferTarget = GLBufferTarget.ARRAY,
) -> None:
    """Upload float vertex/attribute data to the bound buffer."""
    gl_buffer_data(
        buffer_target,
        len(data) * 4,
        (GLfloat * len(data)),
        GLUsageHint.STATIC_DRAW,
    )


def gl_upload_ushort_buffer(
    data: list[int],
    buffer_target: GLBufferTarget = GLBufferTarget.ELEMENT,
) -> None:
    """Upload unsigned-short index data to the bound element buffer."""
    gl_buffer_data(
        buffer_target,
        len(data) * 2,
        (GLushort * len(data)),
        GLUsageHint.STATIC_DRAW,
    )
