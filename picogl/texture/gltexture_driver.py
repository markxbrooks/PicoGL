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

from OpenGL.GL import glGenTextures
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture, glDeleteTextures
from picogl.backend.gl.enums import GLNumeric
from picogl.backend.gl.wrappers import (
    gl_generate_mipmap,
    gl_tex_parameter,
    gl_teximage2d,
)
from picogl.texture.gltexture import GLTexture
from picogl.texture.mapping import FILTER_MAP, FORMAT_MAP, WRAP_MAP
from picogl.texture.texture2d import Texture2D


class GLTextureDriver:
    """gl Texture 2d"""

    @staticmethod
    def create(tex: Texture2D):
        """create"""
        tex.handle = glGenTextures(1)

    @staticmethod
    def bind(tex: Texture2D):
        """bind"""
        glBindTexture(GLTexture.TEXTURE_2D, tex.handle)

    @staticmethod
    def ensure_initialized(tex: Texture2D):
        if not tex.initialized:
            GLTextureDriver.initialize(tex)
            tex.initialized = True

    @staticmethod
    def unbind():
        """bind"""
        glBindTexture(GLTexture.TEXTURE_2D, 0)

    @staticmethod
    def initialize(tex: Texture2D):
        """initialize"""
        GLTextureDriver.bind(tex)

        spec = tex.spec

        internal_format = FORMAT_MAP[spec.format]
        min_filter = FILTER_MAP[spec.min_filter]
        mag_filter = FILTER_MAP[spec.mag_filter]
        wrap_s = WRAP_MAP[spec.wrap_s]
        wrap_t = WRAP_MAP[spec.wrap_t]

        gl_teximage2d(
            target=GLTexture.TEXTURE_2D,
            level=0,
            internalformat=internal_format,
            width=spec.width,
            height=spec.height,
            border=0,
            format=internal_format,
            num_type=GLNumeric.UNSIGNED_BYTE,
            data=tex.data,
        )

        gl_tex_parameter(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MIN_FILTER, min_filter)
        gl_tex_parameter(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MAG_FILTER, mag_filter)
        gl_tex_parameter(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_S, wrap_s)
        gl_tex_parameter(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_T, wrap_t)

        if spec.min_filter == "mipmap":
            gl_generate_mipmap()

    @staticmethod
    def delete(tex: Texture2D):
        """delete"""
        if tex.handle is not None:
            glDeleteTextures([tex.handle])
            tex.handle = None
            tex.initialized = False
