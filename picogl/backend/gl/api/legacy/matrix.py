"""
A context manager for handling OpenGL matrix stack operations.

This module provides a utility function that ensures the proper management
of the OpenGL matrix stack, such as pushing and automatically restoring
the matrix state within a given context.
"""
from contextlib import contextmanager

from backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.enums.legacy.scale import gl_pop_matrix, gl_push_matrix


@contextmanager
def gl_pushed_matrix():
    """Push and automatically restore the current matrix."""
    gl_push_matrix() # push the current matrix to the current stack
    try:
        yield
    finally:
        gl_pop_matrix()


@contextmanager
def gl_matrix_mode():
    """gl matrix mode"""
    set_matrix_mode(GLLegacyMatrixMode.PROJECTION)
    try:
        gl_load_identity()
        yield
    finally:
        set_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
