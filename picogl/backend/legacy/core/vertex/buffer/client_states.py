"""
Legacy Client States context manager
"""

from contextlib import contextmanager

from OpenGL.GL import (GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, glBindBuffer,
                       glDisableClientState, glEnableClientState)


@contextmanager
def legacy_client_states(*states):
    """Enable/disable fixed-function client states safely."""
    for s in states:
        glEnableClientState(s)
    try:
        yield
    finally:
        # Disable in reverse order and unbind both array buffers
        for s in reversed(states):
            glDisableClientState(s)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
