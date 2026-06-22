"""
Module for managing OpenGL texture creation, binding, and deletion.

This module provides the functionality for creating, binding, and deleting
2D textures using OpenGL. It leverages low-level OpenGL functions as well as
custom driver and utility classes to abstract and simplify texture management.
"""

from OpenGL.GL import glDeleteTextures
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D

from picogl.texture.gltexture_driver import GLTextureDriver
from picogl.texture.texture2d import Texture2D
from picogl.texture.texture_spec import TextureSpec
from picogl.wrappers.texture import gl_bind_texture


class GLTextureSystem:
    """Texture creation, binding, and deletion."""

    def __init__(self, driver: GLTextureDriver | None = None):
        self.driver = driver or GLTextureDriver()

    def create_texture(self, width, height, data) -> int:
        spec = TextureSpec(width=width, height=height)
        tex = Texture2D(spec, data)
        self.driver.create(tex)
        self.driver.bind(tex)
        self.driver.initialize(tex)
        return tex.handle

    @staticmethod
    def bind_texture(texture_id):
        gl_bind_texture(texture_id, GL_TEXTURE_2D)

    @staticmethod
    def delete_texture(tex_id: int):
        glDeleteTextures([tex_id])
