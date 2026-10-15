"""
Enumeration of OpenGL framebuffer attachment types.

This module defines framebuffer attachment points used in OpenGL to specify
color, depth, and stencil buffer locations. It is particularly useful when
configuring framebuffers for rendering processes.
"""

from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_NONE, GL_TEXTURE
from OpenGL.raw.GL.VERSION.GL_3_0 import (
    GL_COLOR_ATTACHMENT0,
    GL_COLOR_ATTACHMENT1,
    GL_COLOR_ATTACHMENT2,
    GL_COLOR_ATTACHMENT3,
    GL_DEPTH_ATTACHMENT,
    GL_DEPTH_STENCIL_ATTACHMENT,
    GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,
    GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,
    GL_FRAMEBUFFER_DEFAULT,
    GL_RENDERBUFFER,
    GL_STENCIL_ATTACHMENT,
)


class GLFrameBufferAttachment(IntEnum):
    """GLFramebufferAttachment"""

    COLOR0 = GL_COLOR_ATTACHMENT0
    COLOR1 = GL_COLOR_ATTACHMENT1
    COLOR2 = GL_COLOR_ATTACHMENT2
    COLOR3 = GL_COLOR_ATTACHMENT3
    DEPTH = GL_DEPTH_ATTACHMENT
    STENCIL = GL_STENCIL_ATTACHMENT
    DEPTH_STENCIL = GL_DEPTH_STENCIL_ATTACHMENT


class GLFrameBufferAttachmentParameter(IntEnum):
    """``pname`` values for ``glGetFramebufferAttachmentParameteriv``."""

    OBJECT_TYPE = GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE
    OBJECT_NAME = GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME


class GLFrameBufferObjectType(IntEnum):
    """``GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE`` result values."""

    NONE = GL_NONE
    RENDERBUFFER = GL_RENDERBUFFER
    TEXTURE = GL_TEXTURE
    FRAMEBUFFER_DEFAULT = GL_FRAMEBUFFER_DEFAULT
