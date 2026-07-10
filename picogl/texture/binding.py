"""Provides a context manager for binding a texture in OpenGL.

This module allows temporary binding of a texture in an OpenGL context,
ensuring that the original binding is restored afterwards. It helps manage
state changes when working with OpenGL textures.
"""

from contextlib import contextmanager

from picogl.backend.gl.wrappers import gl_get_integerv
from picogl.backend.gl.wrappers import gl_bind_texture
from texture.gltexture import GLTexture


@contextmanager
def gl_bound_texture(texture_id: int, target: GLTexture = GLTexture.TEXTURE_2D):
    """bound texture"""
    previous = gl_get_integerv(target)
    gl_bind_texture(tex_id=texture_id, target=target)
    try:
        yield
    finally:
        gl_bind_texture(tex_id=previous, target=previous)
