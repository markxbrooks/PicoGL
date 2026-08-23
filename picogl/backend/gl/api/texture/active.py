from __future__ import annotations

from typing import TYPE_CHECKING

from OpenGL.raw.GL.VERSION.GL_1_3 import GL_TEXTURE0, glActiveTexture

if TYPE_CHECKING:
    from picogl.texture.gltexture import GLTexture


def gl_active_texture(texture: int | GLTexture) -> None:
    """Issue ``glActiveTexture``."""
    glActiveTexture(int(texture))


def gl_get_active_texture0() -> None:
    """Select texture unit 0."""
    gl_active_texture(GL_TEXTURE0)
