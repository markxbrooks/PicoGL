"""get gl information for printing"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RENDERER, GL_VENDOR, GL_VERSION
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_SHADING_LANGUAGE_VERSION

from picogl.backend.gl.api.string import gl_get_string


def get_gl_info():
    """Get picogl info"""
    info = """
        Vendor: {0}
        RendererBase: {1}
        OpenGL Version: {2}
        Shader Version: {3}
        """.format(
        gl_get_string(GL_VENDOR).decode(),
        gl_get_string(GL_RENDERER).decode(),
        gl_get_string(GL_VERSION).decode(),
        gl_get_string(GL_SHADING_LANGUAGE_VERSION).decode(),
    )
    return info
