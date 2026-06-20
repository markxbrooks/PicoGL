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

from enum import IntEnum
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_LINEAR,
    GL_REPEAT,
    GL_LINEAR_MIPMAP_LINEAR,
)

class GLTexParam(IntEnum):
    """GL Parameter"""
    REPEAT = GL_REPEAT
    LINEAR = GL_LINEAR
    LINEAR_MIPMAP_LINEAR = GL_LINEAR_MIPMAP_LINEAR
