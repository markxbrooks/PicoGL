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

from numpy import ndarray

from picogl.texture.texture_spec import TextureSpec


class Texture2D:
    """Texture 2D"""

    def __init__(self, spec: TextureSpec, data: ndarray | None = None):
        self.spec = spec
        self.data = data
        self.handle = None  # assigned by backend
        self.initialized = False
