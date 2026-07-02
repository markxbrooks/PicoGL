"""
A collection of OpenGL utility functions for texture and framebuffer operations.

This module provides functions to interact with OpenGL textures and framebuffers,
enabling creation, binding, parameter setting, and more. These functions serve
as a high-level interface for the corresponding OpenGL API calls.

Functions:
- gl_active_texture: Activates a given texture unit.
- gl_get_active_texture0: Activates texture unit 0.
- gl_gen_textures: Generates texture names.
- gl_bind_texture: Binds a texture to a target.
- gl_compressed_tex_image: Specifies a two-dimensional compressed texture image.
- gl_teximage2d: Specifies a two-dimensional texture image.
- gl_teximage3d: Specifies a three-dimensional texture image.
- gl_tex_parameter: Sets texture parameters.
- gl_generate_mipmap: Generates mipmap levels for the current texture.
- gl_framebuffer_texture_2d: Attaches a texture to a framebuffer.

"""

from __future__ import annotations

from array import array
from typing import Union

import numpy as np
from OpenGL.constant import (
    Constant,
    FloatConstant,
    IntConstant,
    LongConstant,
    StringConstant,
)
from OpenGL.GL import (
    glActiveTexture,
    glBindTexture,
    glCompressedTexImage2D,
    glGenerateMipmap,
    glGenTextures,
    glTexImage2D,
    glTexParameteri,
)
from OpenGL.raw.GL.VERSION.GL_1_2 import glTexImage3D
from OpenGL.raw.GL.VERSION.GL_3_0 import glFramebufferTexture2D

from picogl.backend.gl.enums import GLNumeric
from picogl.backend.gl.enums.target.frame_buffer import GLFrameBufferTarget
from picogl.texture.gltexparam import GLTexParam
from picogl.texture.gltexture import GLTexture


def gl_active_texture(texture: GLTexture) -> None:
    """Issue ``glActiveTexture``."""
    glActiveTexture(texture)


def gl_get_active_texture0() -> None:
    """Select texture unit 0."""
    gl_active_texture(GLTexture.TEXTURE0)


def gl_gen_textures(number: int = 1) -> int:
    """Issue ``glGenTextures``."""
    result = glGenTextures(number)
    if number == 1:
        if hasattr(result, "__len__") and not isinstance(result, (int, np.integer)):
            return int(result[0])
        return int(result)
    return result


def gl_bind_texture(tex_id: int, target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Issue ``glBindTexture``."""
    glBindTexture(target, tex_id)


def gl_compressed_tex_image(
    byte_array: array[int],
    gl_format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    h: int,
    level: int,
    size: int,
    w: int,
) -> None:
    """Issue ``glCompressedTexImage2D`` for a 2D texture."""
    glCompressedTexImage2D(
        GLTexture.TEXTURE_2D,
        level,
        gl_format,
        w,
        h,
        0,
        size,
        byte_array,
    )


def gl_teximage2d(
    target: int,
    level: int,
    internalformat: (
        FloatConstant | IntConstant | LongConstant | StringConstant | Constant
    ),
    width: int,
    height: int,
    border: int,
    format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    num_type: int = GLNumeric.UNSIGNED_BYTE,
    data: bytes | np.ndarray | None = None,
) -> None:
    """Issue ``glTexImage2D``."""
    glTexImage2D(
        target,
        level,
        internalformat,
        width,
        height,
        border,
        format,
        num_type,
        data,
    )


def gl_teximage3d(
    target: int,
    level: int,
    internalformat: (
        FloatConstant | IntConstant | LongConstant | StringConstant | Constant
    ),
    width: int,
    height: int,
    depth: int,
    border: int,
    format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    num_type: int,
    data: bytes | np.ndarray | None = None,
) -> None:
    """Issue ``glTexImage3D``."""
    glTexImage3D(
        target,
        level,
        internalformat,
        width,
        height,
        depth,
        border,
        format,
        num_type,
        data,
    )


def gl_tex_parameter(target: int, pname: GLTexture, param: Union[GLTexParam, GLTextureClamp]) -> None:
    """Issue ``glTexParameteri``."""
    glTexParameteri(target, pname, param)


def gl_generate_mipmap(target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Generate mipmaps for the currently bound texture."""
    glGenerateMipmap(target)


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
