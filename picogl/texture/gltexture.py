"""
This module provides functionality for managing 2D OpenGL textures.

It includes a class for creating, binding, uploading data, setting parameters, generating mipmaps, and deleting
2D textures in OpenGL. This class ensures efficient management of texture resources in graphics applications.
"""

from OpenGL.GL import glGenTextures, glTexImage2D
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RGB, glTexParameteri, GL_LINEAR
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture, glDeleteTextures
from OpenGL.raw.GL.VERSION.GL_1_2 import GL_CLAMP_TO_EDGE
from OpenGL.raw.GL._types import GL_UNSIGNED_BYTE
from numpy import ndarray

from picogl.state.texture import GLTexture

from dataclasses import dataclass

@dataclass(frozen=True)
class TextureSpec:
    width: int
    height: int
    format: str = "rgb"
    min_filter: str = "linear"
    mag_filter: str = "linear"
    wrap_s: str = "clamp"
    wrap_t: str = "clamp"


class Texture2D:
    def __init__(self, spec: TextureSpec, data: ndarray | None = None):
        self.spec = spec
        self.data = data
        self.handle = None  # assigned by backend


class GLTextureDriver:
    """GL Texture 2d"""

    def __init__(self):
        self.format = GL_RGB

    def create(self, tex: Texture2D):
        tex.handle = glGenTextures(1)

    def bind(self, tex: Texture2D):
        glBindTexture(GLTexture.TEXTURE_2D, tex.handle)

    def upload(self, tex: Texture2D):
        glTexImage2D(
            GLTexture.TEXTURE_2D,
            0,
            self.format,
            tex.spec.width,
            tex.spec.height,
            0,
            self.format,
            GL_UNSIGNED_BYTE,
            tex.data,
        )

    def set_parameters(self):
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    def generate_mipmap(self):
        glGenerateMipmap(GLTexture.TEXTURE_2D)

    def delete(self, tex: Texture2D):
        glDeleteTextures([tex.handle])