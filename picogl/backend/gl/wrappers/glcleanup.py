"""
OpenGL Buffer Cleanup Utilities
===============================

This module provides helper functions for safely deleting OpenGL buffer objects,
including vertex buffer objects (VBOs), vertex array objects (VAOs), and dictionaries
of buffer handles. It ensures proper resource cleanup and avoids memory leaks in
graphics applications.

Dependencies:
-------------
- OpenGL (PyOpenGL)
- picogl.backend.modern.core.vertex.base (for VertexBuffer type)

Functions:
----------

.. autofunction:: delete_dict_buffers
    Deletes all buffer handles stored in a dictionary and clears the dictionary.

.. autofunction:: delete_buffer_object
    Deletes a buffer object if it is valid and has a non-zero handle.

.. autofunction:: delete_buffer
    Deletes a raw buffer handle if it is valid.

.. autofunction:: delete_vao
    Deletes a vertex array object (VAO) if it is valid.

Usage Example:
--------------

.. code-block:: python

    delete_buffer_object(my_vertex_buffer)
    delete_vao(my_vao_id)
    delete_dict_buffers(buffer_map)
"""

from typing import Any, Dict, Optional

from OpenGL.GL import glDeleteBuffers, glDeleteVertexArrays


def _gl_context_ok() -> bool:
    """True when OpenGL deletes are safe (current, valid context)."""
    try:
        from picogl.backend.modern.core.shader.context import gl_context_available

        return gl_context_available()
    except Exception:
        pass
    try:
        from PySide6.QtGui import QOpenGLContext

        ctx = QOpenGLContext.currentContext()
        return ctx is not None and ctx.isValid()
    except Exception:
        return False


def gl_release_vertex_array_object(vao: Any) -> None:
    """Delete a VAO and any VBOs/EBO registered on it (context-safe no-op if none)."""
    if vao is None or not _gl_context_ok():
        return
    delete_bufs = getattr(vao, "delete_buffers", None)
    if callable(delete_bufs):
        try:
            delete_bufs()
        except Exception:
            pass
    handle = getattr(vao, "handle", None)
    if handle is not None and int(handle) > 0:
        gl_delete_vertex_arrays(int(handle))
        try:
            vao.handle = None
        except Exception:
            pass


def gl_delete_dict_buffers(buffer_dict: Dict[str, int]) -> None:
    """
    delete_dict_buffers

    :param buffer_dict:
    :return:
    """
    for buf in buffer_dict.values():
        gl_delete_buffers(buf)
    buffer_dict.clear()


def gl_delete_buffer_object(buffer: Optional["VertexBuffer"]) -> None:
    """
    delete_buffer_object

    :param buffer: Optional[int]
    :return: None
    """
    if buffer is None or not _gl_context_ok():
        return
    release_vao = getattr(buffer, "delete_buffers", None)
    if callable(release_vao) and hasattr(buffer, "handle"):
        gl_release_vertex_array_object(buffer)
        return
    handle = getattr(buffer, "handle", buffer)
    if handle is not None and int(handle) > 0:
        glDeleteBuffers(1, [int(handle)])


def gl_delete_buffers(buffer: Optional[int]) -> None:
    """
    gl_delete_buffers

    :param buffer: Optional[int]
    :return: None
    """
    if not _gl_context_ok():
        return
    if buffer is not None and buffer > 0:
        glDeleteBuffers(1, [buffer])


def gl_delete_vertex_arrays(vao: Optional[int], number: int = 1) -> None:
    """
    delete_vao

    :param vao: Optional[int]
    :param number: Optional[int]
    :return: None
    """
    if not _gl_context_ok():
        return
    if vao is not None and vao > 0:
        glDeleteVertexArrays(number, [vao])
