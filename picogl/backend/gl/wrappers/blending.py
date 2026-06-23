"""
blending
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glBlendFunc


def gl_blend_func(src, dst):
    glBlendFunc(src, dst)
