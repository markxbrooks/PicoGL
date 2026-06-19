"""
Legacy client state
"""
from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_1 import glDisableClientState, glEnableClientState

from picogl.state.client import GLClientState


def gl_disable_legacy_client_state(state: GLClientState):
    """gl disable client state"""
    glDisableClientState(state)


def gl_enable_legacy_client_state(state: GLClientState):
    """gl legacy client state"""
    glEnableClientState(state)
