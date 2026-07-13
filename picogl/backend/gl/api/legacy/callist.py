"""
GL Call list
"""
from OpenGL.raw.GL.VERSION.GL_1_0 import glCallList


def gl_call_list(call_list):
    """gl call list"""
    glCallList(call_list)
