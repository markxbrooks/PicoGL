"""
Retrieve the OpenGL version from the current context.

This function utilizes the OpenGL library to fetch and return the current
OpenGL version string, which provides information about the version of the
OpenGL implementation in use.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_VERSION

from picogl.backend.gl.api.string import gl_get_string


def gl_get_version() -> str:
    """gl get version"""
    version = gl_get_string(GL_VERSION)
    return version
