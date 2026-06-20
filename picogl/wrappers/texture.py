"""
Texture Loader
"""

from array import array
from typing import Literal

from OpenGL.GL import (
    glCompressedTexImage2D,
    glTexImage2D,
)
from OpenGL.constant import Constant, FloatConstant, IntConstant, LongConstant, StringConstant

from picogl.texture.gltexture import GLTexture


def gl_compressed_tex_image(byte_array: array[int],
                            gl_format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant, h: int,
                            level: int, size: int, w: int):
    """gl compressed tex image"""
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


def gl_teximage2d(target: Literal[GLTexture.TEXTURE_2D],
                  level: int,
                  internalformat: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
                  width: int,
                  height: int,
                  border: int,
                  format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
                  num_type: int,
                  data: bytes | None):
    """gl teximage 2d """
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
