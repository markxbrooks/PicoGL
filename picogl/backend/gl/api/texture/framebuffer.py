"""
A collection of OpenGL utility functions for texture and framebuffer operations.

This module provides functions to interact with OpenGL texture and framebuffers,
enabling creation, binding, parameter setting, and more. These functions serve
as a high-level interface for the corresponding OpenGL API calls.

Functions:.
- gl_framebuffer_texture_2d: Attaches a texture to a framebuffer.

"""

from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_3_0 import glFramebufferTexture2D
from picogl.backend.gl.enums.target.frame_buffer import GLFrameBufferTarget
from picogl.texture.gltexture import GLTexture


def gl_framebuffer_texture_2d(
    target: GLFrameBufferTarget,
    attachment: float | None,
    textarget: GLTexture,
    texture: int,
    level: int,
) -> None:
    """gl framebuffer texture 2d"""
    glFramebufferTexture2D(
        target=target,
        attachment=attachment,
        textarget=textarget,
        texture=texture,
        level=level,
    )
