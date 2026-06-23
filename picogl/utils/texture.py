"""bind texture array"""

from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D

from picogl.backend.gl.wrappers import gl_bind_texture, gl_get_active_texture0


def bind_texture_array(texture_id: int):
    """
    bind_texture_array

    :param texture_id:
    :return: None
    """
    gl_get_active_texture0()
    gl_bind_texture(texture_id, GL_TEXTURE_2D)
