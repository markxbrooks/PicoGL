"""
Device pixel ratio helpers for HiDPI OpenGL surfaces.
"""

from __future__ import annotations

import platform
from typing import Union

from decologr import Decologr as log
from molib.pdb.coordinate.coordinate import Coordinate2D

from picogl.backend.gl.api.framebuffer.parameter import (
    gl_bind_renderbuffer,
    gl_get_framebuffer_attachment_parameteriv,
    gl_get_renderbuffer_parameteriv,
)
from picogl.backend.gl.api.get_integerv import gl_get_integerv
from picogl.backend.gl.api.gl_int import as_gl_int
from picogl.backend.gl.api.texture.bind import gl_bind_texture
from picogl.backend.gl.api.texture.level import gl_get_tex_level_parameteriv
from picogl.backend.gl.enums.frame import (
    GLFrameBufferAttachment,
    GLFrameBufferAttachmentParameter,
    GLFrameBufferObjectType,
)
from picogl.backend.gl.enums.target.frame_buffer import GLFrameBufferTarget
from picogl.backend.gl.enums.target.renderbuffer import (
    GLRenderbufferParameter,
    GLRenderbufferTarget,
)
from picogl.texture.gltexlevel import GLTexLevelParameter
from picogl.texture.gltexture import GLTexture
from picoui.dimensions import Dimensions


def get_dpr() -> int:
    """Return a platform heuristic device-pixel ratio for viewport setup.

    Prefer :func:`device_pixel_ratio` when an OpenGL context is current and
    the logical widget size is known.
    """
    if platform.system() == "Darwin":
        return 2
    return 1


def framebuffer_attachment_size(
        *,
        target: GLFrameBufferTarget = GLFrameBufferTarget.FRAMEBUFFER,
        attachment: GLFrameBufferAttachment = GLFrameBufferAttachment.COLOR0,
) -> tuple[int, int] | None:
    """Return the color-attachment size in pixels, or ``None`` if unsupported.

    Must be called while an OpenGL context is current.
    """
    parameter_name = GLFrameBufferAttachmentParameter.OBJECT_TYPE
    object_type = _gl_get_framebuffer_parameter(attachment, parameter_name, target)
    parameter_name = GLFrameBufferAttachmentParameter.OBJECT_NAME
    object_name = _gl_get_framebuffer_parameter(attachment, parameter_name, target)

    if object_type == GLFrameBufferObjectType.RENDERBUFFER:
        previous = as_gl_int(gl_get_integerv(GLRenderbufferParameter.BINDING))
        try:
            gl_bind_renderbuffer(object_name, GLRenderbufferTarget.RENDERBUFFER)
            width = gl_get_renderbuffer_parameteriv(
                GLRenderbufferTarget.RENDERBUFFER,
                GLRenderbufferParameter.WIDTH,
            )
            height = gl_get_renderbuffer_parameteriv(
                GLRenderbufferTarget.RENDERBUFFER,
                GLRenderbufferParameter.HEIGHT,
            )
        finally:
            gl_bind_renderbuffer(previous, GLRenderbufferTarget.RENDERBUFFER)
        return width, height

    if object_type == GLFrameBufferObjectType.TEXTURE:
        previous = as_gl_int(gl_get_integerv(GLTexture.TEXTURE_BINDING_2D))
        try:
            gl_bind_texture(object_name, GLTexture.TEXTURE_2D)
            width = gl_get_tex_level_parameteriv(
                GLTexture.TEXTURE_2D,
                0,
                GLTexLevelParameter.WIDTH,
            )
            height = gl_get_tex_level_parameteriv(
                GLTexture.TEXTURE_2D,
                0,
                GLTexLevelParameter.HEIGHT,
            )
        finally:
            gl_bind_texture(previous, GLTexture.TEXTURE_2D)
        return width, height

    log.warning(
        f"Cannot determine framebuffer size: "
        f"unsupported color attachment type {object_type}"
    )
    return None


def _gl_get_framebuffer_parameter(attachment: GLFrameBufferAttachment,
                                  parameter_name: Union[GLFrameBufferAttachmentParameter.OBJECT_TYPE,
                                  GLFrameBufferAttachmentParameter.OBJECT_NAME],
                                  target: GLFrameBufferTarget) -> int:
    return gl_get_framebuffer_attachment_parameteriv(
        target,
        attachment,
        parameter_name,
    )


def device_pixel_ratio(
        logical_size: Dimensions,
        *,
        target: GLFrameBufferTarget = GLFrameBufferTarget.FRAMEBUFFER,
        attachment: GLFrameBufferAttachment = GLFrameBufferAttachment.COLOR0,
) -> float:
    """Estimate effective DPR from the OpenGL framebuffer.

    Must be called while an OpenGL context is current.

    :param logical_size: Widget size in logical (CSS / Qt) pixels
        (``logical_size.width`` / ``logical_size.height``).
    :param target: Framebuffer target to query.
    :param attachment: Color attachment point to measure.
    :returns: Average of width and height scale factors, or ``1.0`` on failure.
    """
    logical_width = int(logical_size.width)
    logical_height = int(logical_size.height)
    if logical_width <= 0 or logical_height <= 0:
        return 1.0

    size = framebuffer_attachment_size(target=target, attachment=attachment)
    if size is None:
        return 1.0

    framebuffer_width, framebuffer_height = size
    if framebuffer_width <= 0 or framebuffer_height <= 0:
        return 1.0

    scale_x = framebuffer_width / logical_size.width
    scale_y = framebuffer_height / logical_size.height
    effective = Coordinate2D(x=scale_x, y=scale_y)

    log.message(
        f"Framebuffer={framebuffer_width}x{framebuffer_height}, "
        f"logical={logical_size.width}x{logical_size.height}, "
        f"effective scale=({effective.x:.4f}, {effective.y:.4f})",
        silent=True,
    )

    return (effective.x + effective.y) / 2.0
