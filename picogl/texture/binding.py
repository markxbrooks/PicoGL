"""Provides a context manager for binding a texture in OpenGL.

This module allows temporary binding of a texture in an OpenGL context,
ensuring that the original binding is restored afterwards. It helps manage
state changes when working with OpenGL texture.
"""

from contextlib import contextmanager

from picogl.backend.gl.api import gl_bind_texture, gl_get_integerv
from picogl.backend.gl.api.gl_int import as_gl_int
from picogl.texture.gltexture import GLTexture


@contextmanager
def gl_bound_texture(texture_id: int, target: GLTexture = GLTexture.TEXTURE_2D):
    """Bind ``texture_id`` to ``target``, restoring the previous binding on exit."""
    previous = as_gl_int(gl_get_integerv(GLTexture.TEXTURE_BINDING_2D))
    gl_bind_texture(tex_id=int(texture_id), target=target)
    try:
        yield
    finally:
        gl_bind_texture(tex_id=previous, target=target)
