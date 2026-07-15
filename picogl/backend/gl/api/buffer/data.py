"""
Provides a function to bind GPU buffer data using OpenGL.

This module defines a utility function to wrap the OpenGL `glBufferData`
call, which uploads data to a specified buffer object in GPU memory. The
function enforces checks to ensure valid arguments and simplifies the usage
of OpenGL buffer operations by abstracting certain details.
"""

from OpenGL.GL import glBufferData

from picogl.backend.gl.enums import GLBufferTarget, GLUsageHint


def gl_buffer_data(
    target: GLBufferTarget = GLBufferTarget.ARRAY,
    size: int = 0,
    data=None,
    usage_hint: GLUsageHint = GLUsageHint.STATIC_DRAW,
):
    """gl bind buffer"""
    assert data is not None
    assert size > 0
    glBufferData(target, size, data, usage_hint)
