from __future__ import annotations

from array import array
from dataclasses import dataclass
from typing import Union

import numpy as np
from OpenGL.constant import (Constant, FloatConstant, IntConstant,
                             LongConstant, StringConstant)
from OpenGL.GL import glCompressedTexImage2D, glTexImage2D
from OpenGL.raw.GL.VERSION.GL_1_2 import glTexImage3D

from picogl.backend.gl.enums import GLNumeric
from picogl.texture.gltexture import GLTexture

ConstantType = Union[FloatConstant, IntConstant, LongConstant, StringConstant, Constant]
CompressedTexData = Union[bytes, bytearray, memoryview, array, np.ndarray]


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
    byte_array: CompressedTexData


def _as_compressed_payload(data: CompressedTexData) -> bytes | np.ndarray:
    """Normalize compressed texel bytes for PyOpenGL's data converter."""
    if isinstance(data, np.ndarray):
        return np.ascontiguousarray(data, dtype=np.uint8)
    if isinstance(data, memoryview):
        return data.tobytes()
    if isinstance(data, array):
        return bytes(data)
    return bytes(data)


def gl_teximage2d_from_params(
    params: TexImageParams, target: int = GLTexture.TEXTURE_2D
) -> None:
    """Issue ``glTexImage2D``."""
    glTexImage2D(
        target,
        params.level,
        params.internalformat,
        params.width,
        params.height,
        params.border,
        params.format,
        params.num_type,
        params.data,
    )


def gl_teximage3d_from_params(
    params: TexImage3DParams, target: int = GLTexture.TEXTURE_2D
) -> None:
    """Issue ``glTexImage3D``."""
    glTexImage3D(
        target,
        params.level,
        params.internalformat,
        params.width,
        params.height,
        params.depth,
        params.border,
        params.format,
        params.num_type,
        params.data,
    )


def gl_compressed_tex_image_from_params(params: CompressedTexImageParams) -> None:
    """Issue ``glCompressedTexImage2D`` for a 2D texture."""
    gl_compressed_tex_image(
        params.byte_array,
        params.gl_format,
        params.height,
        params.level,
        params.size,
        params.width,
    )


def gl_compressed_tex_image(
    byte_array: CompressedTexData,
    gl_format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    height: int,
    level: int,
    size: int,
    width: int,
) -> None:
    """Issue ``glCompressedTexImage2D`` for a 2D texture.

    PyOpenGL's wrapped ``glCompressedTexImage2D`` omits ``imageSize`` and
    derives it from ``data``. Passing an explicit size as the 7th argument
    makes PyOpenGL treat that int as the data pointer and raises
    ``NumberHandler`` / ``arrayByteCount``.
    """
    payload = _as_compressed_payload(byte_array)
    if size and len(payload) < size:
        raise ValueError(
            f"Compressed texture payload too small: need {size} bytes, got {len(payload)}"
        )
    # Pass only the texel payload; do not pass imageSize.
    glCompressedTexImage2D(
        int(GLTexture.TEXTURE_2D),
        int(level),
        gl_format,
        int(width),
        int(height),
        0,
        payload[:size] if size else payload,
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
    byte_array: CompressedTexData,
    gl_format: FloatConstant | IntConstant | LongConstant | StringConstant | Constant,
    h: int,
    level: int,
    size: int,
    w: int,
) -> None:
    """Alias for :func:`gl_compressed_tex_image`."""
    gl_compressed_tex_image(byte_array, gl_format, h, level, size, w)
