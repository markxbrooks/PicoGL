"""
gl_light_fv
"""

from OpenGL.GL import glLightfv
from picogl.backend.gl.state.fill import (
    GLLight,
    GLLightParameter,
)

from picogl.backend.state import gl_value


def gl_light_fv(light: GLLight, param: GLLightParameter, position) -> None:
    """
    gl_light_fv
    """
    glLightfv(gl_value(light), param, position)