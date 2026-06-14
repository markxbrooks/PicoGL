"""
This module provides functionality for managing 2D OpenGL textures.

It includes a class for creating, binding, uploading data, setting parameters, generating mipmaps, and deleting
2D textures in OpenGL. This class ensures efficient management of texture resources in graphics applications.

Example Usage:
==============

  >>  spec = TextureSpec(width=width, height=height)
  >>  tex = Texture2D(spec, data)
  >>  driver = GLTextureDriver()
  >>  driver.create(tex)
  >>  driver.bind(tex)
  >>  driver.set_parameters()
  >>  driver.upload(tex)
  >>  driver.generate_mipmap()
  >>  return tex.handle

"""
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum

from numpy import ndarray
from OpenGL.GL import glGenTextures, glTexImage2D
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.raw.GL._types import GL_UNSIGNED_BYTE
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_LINEAR, GL_RGB,
                                          GL_TEXTURE_MAG_FILTER,
                                          GL_TEXTURE_MIN_FILTER,
                                          GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
                                          glTexParameteri)
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture, glDeleteTextures
from OpenGL.raw.GL.VERSION.GL_1_2 import GL_CLAMP_TO_EDGE
from OpenGL.raw.GL.VERSION.GL_1_3 import (GL_ACTIVE_TEXTURE, GL_TEXTURE0,
                                          glActiveTexture)
from OpenGL.raw.GL.VERSION.GL_4_5 import GL_TEXTURE_BINDING_2D
from picogl.state.param import GLParam
from picogl.state.query import GLStateQuery

FORMAT_MAP = {
    "rgb": GL_RGB,
}

FILTER_MAP = {
    "linear": GL_LINEAR,
}

WRAP_MAP = {
    "clamp": GL_CLAMP_TO_EDGE,
}

@dataclass(frozen=True)
class TextureSpec:
    """Texture Spec"""
    width: int
    height: int
    format: str = "rgb"
    min_filter: str = "linear"
    mag_filter: str = "linear"
    wrap_s: str = "clamp"
    wrap_t: str = "clamp"


class Texture2D:
    """Texture 2D"""
    def __init__(self, spec: TextureSpec, data: ndarray | None = None):
        self.spec = spec
        self.data = data
        self.handle = None  # assigned by backend
        self.initialized = False


class GLTextureDriver:
    """GL Texture 2d"""

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

        glTexImage2D(
            GLTexture.TEXTURE_2D,
            0,
            internal_format,
            spec.width,
            spec.height,
            0,
            internal_format,
            GL_UNSIGNED_BYTE,
            tex.data,
        )

        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MIN_FILTER, min_filter)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MAG_FILTER, mag_filter)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_S, wrap_s)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_T, wrap_t)

        if spec.min_filter == "mipmap":
            glGenerateMipmap(GLTexture.TEXTURE_2D)

    @staticmethod
    def delete(tex: Texture2D):
        """delete"""
        if tex.handle is not None:
            glDeleteTextures([tex.handle])
            tex.handle = None
            tex.initialized = False


class GLTexture(IntEnum):
    """GL Texture Mode"""
    TEXTURE_2D = GL_TEXTURE_2D
    TEXTURE_BINDING_2D = GL_TEXTURE_BINDING_2D
    TEXTURE_MIN_FILTER = GL_TEXTURE_MIN_FILTER
    TEXTURE_MAG_FILTER = GL_TEXTURE_MAG_FILTER
    TEXTURE_WRAP_S = GL_TEXTURE_WRAP_S
    TEXTURE_WRAP_T = GL_TEXTURE_WRAP_T
    TEXTURE0 = GL_TEXTURE0
    ACTIVE_TEXTURE = GL_ACTIVE_TEXTURE

    @classmethod
    def choices(cls):
        return [m.value for m in cls]

    @staticmethod
    def set_active(unit=TEXTURE0):
        glActiveTexture(unit)

    @staticmethod
    def bind(target: int, texture: int):
        glBindTexture(target, texture)

    @staticmethod
    @contextmanager
    def bound_texture(texture_id: int, unit: int = GL_TEXTURE0):
        """
        Bind a texture to a specific unit, restoring previous state.
        """

        state = GLStateQuery()

        # 1. Save currently active unit (GL_TEXTUREi enum)
        prev_active = state.get(GLParam.ACTIVE_TEXTURE)

        try:
            # 2. Switch to requested unit
            GLTexture.set_active(unit)

            # 3. NOW read binding for this unit
            prev_binding = state.get(GLParam.TEXTURE_BINDING_2D)

            # 4. Bind new texture
            GLTexture.bind(GL_TEXTURE_2D, texture_id or 0)

            yield

        finally:
            # Restore binding on the SAME unit
            GLTexture.bind(GL_TEXTURE_2D, prev_binding)

            # Restore previously active unit
            GLTexture.set_active(prev_active)