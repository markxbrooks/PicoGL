"""
setup clamp-to-edge textures mapping
"""

from picogl.backend.gl.api import gl_tex_parameter
from picogl.core.texture_clamp import GLTextureClamp
from picogl.texture.gltexparam import GLTexParam
from picogl.texture.gltexture import GLTexture


def setup_clamped_linear_sampling(target: GLTexture = GLTexture.TEXTURE_2D) -> None:
    """Clamp-to-edge, no mipmaps — avoids face-edge bleed on the startup cube."""
    gl_tex_parameter(target, GLTexture.TEXTURE_WRAP_S, GLTextureClamp.TO_EDGE)
    gl_tex_parameter(target, GLTexture.TEXTURE_WRAP_T, GLTextureClamp.TO_EDGE)
    gl_tex_parameter(target, GLTexture.TEXTURE_MAG_FILTER, GLTexParam.LINEAR)
    gl_tex_parameter(target, GLTexture.TEXTURE_MIN_FILTER, GLTexParam.LINEAR)