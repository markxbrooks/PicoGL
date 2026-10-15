"""Framebuffer attachment and renderbuffer API wrappers."""

from picogl.backend.gl.api.framebuffer.parameter import (
    gl_bind_renderbuffer,
    gl_get_framebuffer_attachment_parameteriv,
    gl_get_renderbuffer_parameteriv,
)

__all__ = [
    "gl_bind_renderbuffer",
    "gl_get_framebuffer_attachment_parameteriv",
    "gl_get_renderbuffer_parameteriv",
]
