"""
Typed wrappers for framebuffer attachment and renderbuffer queries.
"""

from __future__ import annotations

from OpenGL.GL import (
    glBindRenderbuffer,
    glGetFramebufferAttachmentParameteriv,
    glGetRenderbufferParameteriv,
)
from picogl.backend.gl.api.gl_int import as_gl_int
from picogl.backend.gl.enums.frame import (
    GLFrameBufferAttachment,
    GLFrameBufferAttachmentParameter,
)
from picogl.backend.gl.enums.target.frame_buffer import GLFrameBufferTarget
from picogl.backend.gl.enums.target.renderbuffer import (
    GLRenderbufferParameter,
    GLRenderbufferTarget,
)


def gl_get_framebuffer_attachment_parameteriv(
    target: GLFrameBufferTarget,
    attachment: GLFrameBufferAttachment,
    pname: GLFrameBufferAttachmentParameter,
) -> int:
    """Issue ``glGetFramebufferAttachmentParameteriv``; return an ``int``."""
    return as_gl_int(
        glGetFramebufferAttachmentParameteriv(int(target), int(attachment), int(pname))
    )


def gl_bind_renderbuffer(
    renderbuffer: int,
    target: GLRenderbufferTarget = GLRenderbufferTarget.RENDERBUFFER,
) -> None:
    """Issue ``glBindRenderbuffer``."""
    glBindRenderbuffer(int(target), int(renderbuffer))


def gl_get_renderbuffer_parameteriv(
    target: GLRenderbufferTarget,
    pname: GLRenderbufferParameter,
) -> int:
    """Issue ``glGetRenderbufferParameteriv``; return an ``int``."""
    return as_gl_int(glGetRenderbufferParameteriv(int(target), int(pname)))
