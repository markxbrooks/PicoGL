"""
Provides functionality to bind a buffer object to a specified target in OpenGL.

This module uses the OpenGL raw binding to interact with OpenGL APIs for
managing buffer objects. The `gl_bind_buffer` function allows the binding of
a given buffer object to a specific target. This is often used in rendering
pipelines to enable operations on buffer objects.

Functions:
- gl_bind_buffer: Binds a buffer object to the specified target.
"""

from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer


def gl_bind_buffer(target: int, ebo_id: int | None):
    """
    Binds a buffer object to a specified binding point in the OpenGL context.

    This function wraps the OpenGL glBindBuffer call, which is used to bind a buffer
    object to the specified target. Once bound, the buffer becomes the active buffer
    for the target, allowing subsequent OpenGL commands to operate on it.

    Parameters:
    target : int
        The target to which the buffer is to be bound. Common examples include
        GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, etc.
    ebo_id : int or None
        The name (ID) of the buffer object to bind. If None is provided, the
        target will be unbound, and no buffer will be associated with it.
    """
    glBindBuffer(target, ebo_id)
