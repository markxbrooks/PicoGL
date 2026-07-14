from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_3 import glActiveTexture

from picogl.texture.gltexture import GLTexture


def gl_active_texture(texture: GLTexture) -> None:
    """Issue ``glActiveTexture``."""
    glActiveTexture(texture)


def gl_get_active_texture0() -> None:
    """Select texture unit 0."""
    gl_active_texture(GLTexture.TEXTURE0)
