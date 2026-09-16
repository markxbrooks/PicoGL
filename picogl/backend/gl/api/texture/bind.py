from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture
from picogl.texture.gltexture import GLTexture


def gl_bind_texture(tex_id: int, target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Issue ``glBindTexture``."""
    glBindTexture(target, tex_id)
