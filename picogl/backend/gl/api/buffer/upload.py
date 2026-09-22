"""Typed helpers for uploading CPU arrays into the currently bound GL buffer."""

from __future__ import annotations

from ctypes import Array
from typing import Sequence

from OpenGL.GL import GLfloat, GLushort
from picogl.backend.gl.api.buffer.data import gl_buffer_data
from picogl.backend.gl.enums import GLBufferTarget, GLUsageHint


def _ctypes_array(ctype, data: Sequence) -> Array:
    """Build a filled ctypes array instance (not an array type)."""
    values = list(data)
    return (ctype * len(values))(*values)


def gl_upload_float_buffer(
    data: list[float],
    buffer_target: GLBufferTarget = GLBufferTarget.ARRAY,
) -> None:
    """Upload float vertex/attribute data to the bound buffer."""
    payload = _ctypes_array(GLfloat, data)
    gl_buffer_data(
        buffer_target,
        len(payload) * 4,
        payload,
        GLUsageHint.STATIC_DRAW,
    )


def gl_upload_ushort_buffer(
    data: list[int],
    buffer_target: GLBufferTarget = GLBufferTarget.ELEMENT,
) -> None:
    """Upload unsigned-short index data to the bound element buffer."""
    payload = _ctypes_array(GLushort, data)
    gl_buffer_data(
        buffer_target,
        len(payload) * 2,
        payload,
        GLUsageHint.STATIC_DRAW,
    )
