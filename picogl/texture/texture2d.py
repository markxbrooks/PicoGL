"""
This module provides functionality for managing 2D OpenGL textures.

It includes a class for creating, binding, uploading data, setting parameters, generating mipmaps, and deleting
2D textures in OpenGL. This class ensures efficient management of texture resources in graphics applications.

Example Usage:
==============

  >> spec = TextureSpec(width=width, height=height)
  >> tex = Texture2D(spec, data)
  >> driver = GLTextureDriver()
  >> driver.create(tex)
  >> driver.bind(tex)
  >> driver.set_parameters()
  >> driver.upload(tex)
  >> driver.generate_mipmap()
  >> return tex.handle

"""
from typing import Any

from picogl.backend.gl.enums import GLNumeric
from picogl.backend.gl.wrappers import gl_gen_textures, gl_teximage2d
from picogl.core.color import GLColor
from numpy import ndarray
from picogl.texture.texture_spec import TextureSpec
from picogl.texture.binding import gl_bound_texture


class Texture2D:
    """Texture 2D"""

    def __init__(self, spec: TextureSpec, data: ndarray | None = None):
        self.spec = spec
        self.data = data
        self.handle = None  # assigned by backend
        self.initialized = False


def upload_texture_2d(target: GLNumeric, texture_buffer: bytes, texture_height: int, texture_width: int) -> Any:
    """
    generate_texture

    :param target: GLNumeric.UNSIGNED_BYTE
    :param texture_buffer: bytes
    :param texture_height: int
    :param texture_width: int
    :return: int
    """
    texture_id = gl_gen_textures(1)
    with gl_bound_texture(texture_id, target):
        gl_teximage2d(
            target=target,
            level=0,
            internalformat=GLColor.SRGB8,
            width=texture_width,
            height=texture_height,
            border=0,
            format=GLColor.RGB,
            num_type=GLNumeric.UNSIGNED_BYTE,
            data=texture_buffer,
        )
    return texture_id