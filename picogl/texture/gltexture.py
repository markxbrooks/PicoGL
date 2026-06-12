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
        self.id = None  # assigned by backend


class GLTextureDriver:
    """GL Texture 2d"""

    def __init__(self):
        self.format = GL_RGB
        self.tex: Texture2D | None = None
        self.id: int | None = None

    def create(self, tex: Texture2D):
        tex.id = glGenTextures(1)
        self.tex = tex
        self.id = int(tex.id)

    def bind(self, tex: Texture2D | None = None):
        tex = tex or self.tex
        if tex is None or tex.id is None:
            raise RuntimeError("Cannot bind texture before create()")
        glBindTexture(GLTexture.TEXTURE_2D, tex.id)

    def upload(self, data: ndarray):
        if self.tex is None:
            raise RuntimeError("Cannot upload texture before create()")
        self.bind(self.tex)
        glTexImage2D(
            GLTexture.TEXTURE_2D,
            0,
            self.format,
            int(self.tex.spec.width),
            int(self.tex.spec.height),
            0,
            self.format,
            GL_UNSIGNED_BYTE,
            data,
        )

    def set_parameters(self):
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GLTexture.TEXTURE_2D, GLTexture.TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    def generate_mipmap(self):
        glGenerateMipmap(GLTexture.TEXTURE_2D)

    def delete(self):
        if self.id is not None:
            glDeleteTextures([self.id])