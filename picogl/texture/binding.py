from contextlib import contextmanager

from picogl.backend.gl.wrappers import gl_bind_texture
from texture.gltexture import GLTexture


@contextmanager
def bound_texture(texture_id: int, target: GLTexture):
    gl_bind_texture(texture_id, target)
    try:
        yield
    finally:
        gl_bind_texture(0, target)