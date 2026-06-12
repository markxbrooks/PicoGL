from OpenGL.GL import glGenTextures, glTexImage2D
from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RGB, glTexParameteri, GL_TEXTURE_MIN_FILTER, GL_LINEAR, \
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture, glDeleteTextures
from OpenGL.raw.GL.VERSION.GL_1_2 import GL_CLAMP_TO_EDGE
from OpenGL.raw.GL._types import GL_UNSIGNED_BYTE
from numpy import ndarray


class GLTexture2D:
    """GL Texture 2d"""
    def __init__(self, width: int, height: int, fmt=GL_RGB):
        self.id = glGenTextures(1)
        self.width = width
        self.height = height
        self.format = fmt

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def upload(self, data: ndarray):
        self.bind()
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            self.format,
            self.width,
            self.height,
            0,
            self.format,
            GL_UNSIGNED_BYTE,
            data,
        )

    def set_parameters(self):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    def generate_mipmap(self):
        glGenerateMipmap(GL_TEXTURE_2D)

    def delete(self):
        glDeleteTextures([self.id])