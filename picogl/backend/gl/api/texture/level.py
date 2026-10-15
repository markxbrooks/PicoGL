"""
Typed wrapper for ``glGetTexLevelParameteriv``.
"""

from __future__ import annotations

from OpenGL.GL import glGetTexLevelParameteriv
from picogl.backend.gl.api.gl_int import as_gl_int
from picogl.texture.gltexlevel import GLTexLevelParameter
from picogl.texture.gltexture import GLTexture


def gl_get_tex_level_parameteriv(
    target: GLTexture,
    level: int,
    pname: GLTexLevelParameter,
) -> int:
    """Issue ``glGetTexLevelParameteriv``; return an ``int``."""
    return as_gl_int(glGetTexLevelParameteriv(int(target), int(level), int(pname)))
