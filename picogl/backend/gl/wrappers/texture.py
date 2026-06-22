"""OpenGL texture upload wrappers (2D and 3D)."""

from __future__ import annotations

from array import array
from typing import Any

import numpy as np
from OpenGL.constant import (Constant, FloatConstant, IntConstant,
                             LongConstant, StringConstant)
from OpenGL.GL import (GL_TEXTURE0, glActiveTexture, glBindTexture,
                       glCompressedTexImage2D, glGenerateMipmap, glGenTextures,
                       glTexImage2D, glTexParameteri)
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_2 import glTexImage3D
from picogl.core.enums.numerical import GLNumeric


def gl_active_texture(unit: int) -> None:
    """Issue ``glActiveTexture``."""
    glActiveTexture(unit)


def gl_get_active_texture0() -> None:
    """Select texture unit 0."""
    gl_active_texture(GL_TEXTURE0)


def gl_gen_textures(number: int = 1) -> Any:
    """Issue ``glGenTextures``."""
    return glGenTextures(number)


def gl_bind_texture(tex_id: int, target: int = GL_TEXTURE_2D) -> None:
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
        GL_TEXTURE_2D,
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


def gl_tex_parameter(target: int, pname: Any, param: Any) -> None:
    """Issue ``glTexParameteri``."""
    glTexParameteri(target, pname, param)


def gl_generate_mipmap(target: int = GL_TEXTURE_2D) -> None:
    """Generate mipmaps for the currently bound texture."""
    glGenerateMipmap(target)
