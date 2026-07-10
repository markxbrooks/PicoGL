"""Provides a context manager for binding a texture in OpenGL.

This module allows temporary binding of a texture in an OpenGL context,
ensuring that the original binding is restored afterwards. It helps manage
state changes when working with OpenGL textures.
"""

from contextlib import contextmanager

from picogl.backend.gl.wrappers import gl_bind_texture, gl_get_integerv
from picogl.texture.gltexture import GLTexture


def _as_gl_int(value) -> int:
    """Normalize glGetIntegerv results (scalar or length-1 array) to int."""
    if hasattr(value, "__len__") and not isinstance(value, (bytes, str)):
        return int(value[0])
    return int(value)


@contextmanager
def gl_bound_texture(texture_id: int, target: GLTexture = GLTexture.TEXTURE_2D):
    """Bind ``texture_id`` to ``target``, restoring the previous binding on exit."""
    previous = _as_gl_int(gl_get_integerv(GLTexture.TEXTURE_BINDING_2D))
    gl_bind_texture(tex_id=int(texture_id), target=target)
    try:
        yield
    finally:
        gl_bind_texture(tex_id=previous, target=target)
