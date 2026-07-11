from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_0 import glTexCoord2f


def gl_tex_coord2f(u, v):
    """gl tex_coord2f"""
    return glTexCoord2f(u, v)
