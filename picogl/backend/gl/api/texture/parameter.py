from __future__ import annotations

from typing import Union

from OpenGL.raw.GL.VERSION.GL_1_0 import glTexParameteri
from picogl.core.texture_clamp import GLTextureClamp
from picogl.texture.gltexparam import GLTexParam
from picogl.texture.gltexture import GLTexture


def gl_tex_parameter(
    target: int, pname: GLTexture, param: Union[GLTexParam, GLTextureClamp]
) -> None:
    """Issue ``glTexParameteri``."""
    glTexParameteri(target, pname, param)
