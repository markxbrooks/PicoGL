"""
blending
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glBlendFunc

# from picogl.backend.gl.capability import GLBlendFactor


def gl_blend_func(src: "GLBlendFactor" , dst: "GLBlendFactor") -> None:
    """gl blend func"""
    glBlendFunc(src, dst)
