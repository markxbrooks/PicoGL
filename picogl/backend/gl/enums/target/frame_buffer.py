"""
Enumeration of OpenGL framebuffer targets.

This module defines an enumeration of OpenGL framebuffer targets
for use with OpenGL functions that interact with framebuffers.
It includes constants for specifying read framebuffer, draw
framebuffer, and general framebuffer targets.
"""

from OpenGL.raw.GL.VERSION.GL_3_0 import GL_FRAMEBUFFER, GL_FRAMEBUFFER_COMPLETE


class GLFrameBufferTarget(IntEnum):
    """GLFrameBufferTarget"""
    FRAMEBUFFER = GL_FRAMEBUFFER # Is equivalent to GL_DRAW_FRAMEBUFFER
    READ_FRAMEBUFFER = GL_READ_FRAMEBUFFER


class GLFrameBufferStatus:
    """GL Framebuffer Status"""
    FRAMEBUFFER_COMPLETE = GL_FRAMEBUFFER_COMPLETE
