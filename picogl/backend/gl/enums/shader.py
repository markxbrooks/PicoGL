from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_2_0 import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER


class GLShader(IntEnum):
    """GL Shader"""
    VERTEX_SHADER = GL_VERTEX_SHADER
    FRAGMENT_SHADER = GL_FRAGMENT_SHADER
