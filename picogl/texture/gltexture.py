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

from contextlib import contextmanager
from enum import IntEnum
from typing import Any

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
)
from OpenGL.raw.GL.VERSION.GL_1_2 import GL_TEXTURE_3D
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_ACTIVE_TEXTURE, GL_TEXTURE0
from OpenGL.raw.GL.VERSION.GL_4_5 import GL_TEXTURE_BINDING_2D
from picogl.backend.gl.state.param import GLParam
from picogl.backend.gl.state.query import GLStateQuery


class GLTexture(IntEnum):
    """gl Texture Mode"""

    TEXTURE_2D = GL_TEXTURE_2D
    TEXTURE_3D = GL_TEXTURE_3D
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
        # Lazy import avoids circular import with picogl.backend.gl.wrappers.texture.
        from picogl.backend.gl.api.texture import gl_active_texture

        gl_active_texture(unit)

    @staticmethod
    def bind(target: int, texture: int):
        from picogl.backend.gl.api.texture import gl_bind_texture

        gl_bind_texture(texture, target)

    @staticmethod
    @contextmanager
    def enabled_texture2d():
        """Texture 2D Enabled"""
        was_enabled = GLTexture.get_enabled_tex2d()
        try:
            if not was_enabled:
                GLTexture.enable_tex2d()
            yield
        finally:
            if not was_enabled:
                GLTexture.disable_tex2d()

    @staticmethod
    def disable_tex2d():
        from picogl.backend.gl.driver.capability import GLCapabilityDriver

        GLCapabilityDriver.disable(GL_TEXTURE_2D)

    @staticmethod
    def enable_tex2d():
        from picogl.backend.gl.driver.capability import GLCapabilityDriver

        GLCapabilityDriver.enable(GL_TEXTURE_2D)

    @staticmethod
    def get_enabled_tex2d(self) -> Any:
        from picogl.backend.gl.driver.capability import GLCapabilityDriver

        return GLCapabilityDriver.is_enabled(GL_TEXTURE_2D)

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
