"""
Legacy Client States context manager
"""

from contextlib import contextmanager

from OpenGL.raw.GL.VERSION.GL_1_1 import glDisableClientState, gl_enableClientState
from OpenGL.raw.GL.VERSION.GL_1_5 import (
    GL_ARRAY_BUFFER,
    GL_ELEMENT_ARRAY_BUFFER,
    glBindBuffer,
)


@contextmanager
def legacy_client_states(*states):
    """Enable/disable fixed-function client states safely."""
    for s in states:
        gl_enableClientState(s)
    try:
        yield
    finally:
        # Disable in reverse order and unbind both array buffers
        for s in reversed(states):
            glDisableClientState(s)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


@contextmanager
def legacy_client_states_old(*states):
    """legacy client states context manager"""
    for state in states:
        gl_enableClientState(state)
    try:
        yield
    finally:
        for state in reversed(states):
            glDisableClientState(state)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
