from __future__ import annotations

from array import array

import numpy as np
from OpenGL.constant import (Constant, FloatConstant, IntConstant,
                             LongConstant, StringConstant)
from OpenGL.GL import glCompressedTexImage2D, glTexImage2D
from OpenGL.raw.GL.VERSION.GL_1_2 import glTexImage3D

from picogl.backend.gl.enums import GLNumeric
from picogl.texture.gltexture import GLTexture


from dataclasses import dataclass
from typing import Union
import numpy as np

ConstantType = Union[FloatConstant, IntConstant, LongConstant, StringConstant, Constant]

@dataclass
class TexImageParams:
    """Parameters for glTexImage operations."""
    level: int
    internalformat: ConstantType
    width: int
    height: int
    border: int
    format: ConstantType
    num_type: int = GLNumeric.UNSIGNED_BYTE
    data: Union[bytes, np.ndarray, None] = None
    
@dataclass
class TexImage3DParams(TexImageParams):
    """Parameters for glTexImage3D operations."""
    depth: int = 0

@dataclass
class CompressedTexImageParams:
    """Parameters for glCompressedTexImage2D operations."""
    level: int
    gl_format: ConstantType
    width: int
    height: int
    size: int
    byte_array: array[int]
    
    

def gl_compressed_tex_image(
    byte_array: array[int],
    gl_format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    height: int,
    level: int,
    size: int,
    width: int,
) -> None:
    """Issue ``glCompressedTexImage2D`` for a 2D texture."""
    glCompressedTexImage2D(
        GLTexture.TEXTURE_2D,
        level,
        gl_format,
        width,
        height,
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
    
def gl_compressed_tex_image_old(
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
