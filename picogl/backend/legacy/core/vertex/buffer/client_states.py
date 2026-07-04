"""
A utility for safely managing fixed-function OpenGL client states.

This module provides a context manager to enable and disable OpenGL
legacy client states in a controlled manner. It ensures that the
client states are reset to their initial state upon exiting the
context, even in the case of an exception.
"""

from contextlib import contextmanager

from OpenGL.GL import GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER
from picogl.backend.gl.wrappers import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.backend.gl.wrappers.buffer import gl_bind_buffer


@contextmanager
def legacy_client_states(*states):
    """Enable/disable fixed-function client states safely."""
    for s in states:
        gl_enable_legacy_client_state(s)
    try:
        yield
    finally:
        for s in reversed(states):
            gl_disable_legacy_client_state(s)
        gl_bind_buffer(GL_ARRAY_BUFFER, 0)
        gl_bind_buffer(GL_ELEMENT_ARRAY_BUFFER, 0)
