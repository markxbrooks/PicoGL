"""OpenGL texture upload wrappers (2D and 3D)."""

from __future__ import annotations

from array import array
from typing import Any

import numpy as np
from OpenGL.GL import (
    glCompressedTexImage2D,
    glGenerateMipmap,
    glTexImage2D,
    glTexParameteri,
)
from OpenGL.constant import Constant, FloatConstant, IntConstant, LongConstant, StringConstant
from OpenGL.GL import glBindTexture, glGenTextures
from OpenGL.raw.GL.VERSION.GL_1_2 import glTexImage3D
from OpenGL.GL import glActiveTexture, GL_TEXTURE0
from picogl.numerical import GLNumeric
from picogl.texture.gltexture import GLTexture


def gl_get_active_texture0():
    glActiveTexture(GL_TEXTURE0)


def gl_gen_textures(number) -> Any:
    """gl gen textures"""
    return glGenTextures(number)


def gl_bind_texture(tex_id: int, target: GLTexture = GLTexture.TEXTURE_2D):
    """gl bind texture (with OpenGL)"""
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
    target: int | GLTexture,
    level: int,
    internalformat: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
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
    target: int | GLTexture,
    level: int,
    internalformat: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
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


def gl_tex_parameter(target: int, pname: Any, param: Any) -> None:
    """Issue ``glTexParameteri``."""
    glTexParameteri(target, pname, param)


def gl_generate_mipmap(target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Generate mipmaps for the currently bound texture."""
    glGenerateMipmap(target)
