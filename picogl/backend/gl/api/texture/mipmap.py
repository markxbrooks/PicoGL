from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_3_0 import glGenerateMipmap

from picogl.texture.gltexture import GLTexture


def gl_generate_mipmap(target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Generate mipmaps for the currently bound texture."""
    glGenerateMipmap(target)
