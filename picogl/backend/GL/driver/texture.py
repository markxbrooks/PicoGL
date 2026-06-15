from OpenGL.GL import glDeleteTextures
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture

from picogl.texture.gltexture import GLTextureDriver, TextureSpec, Texture2D


class GLTextureSystem:
    """Texture creation, binding, and deletion."""

    def __init__(self, driver: GLTextureDriver | None = None):
        self.driver = driver or GLTextureDriver()

    def create_texture(self, width, height, data) -> int:
        spec = TextureSpec(width=width, height=height)
        tex = Texture2D(spec, data)
        self.driver.create(tex)
        self.driver.bind(tex)
        self.driver.initialize(tex)
        return tex.handle

    @staticmethod
    def bind_texture(texture_id):
        glBindTexture(GL_TEXTURE_2D, texture_id)

    @staticmethod
    def delete_texture(tex_id: int):
        glDeleteTextures([tex_id])
