"""
Provides constants for working with fog-related properties in OpenGL.

This module defines the `GLFog` class, which encapsulates fog-related
constants from the OpenGL 1.0 version. These constants can be used
to configure fog parameters, including fog color, start and end
distances, and fog mode.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FOG, GL_FOG_COLOR, GL_FOG_END, GL_FOG_MODE, GL_FOG_START, GL_FOG_INDEX, \
    glFogfv, glFogi, GL_LINEAR, glFogf

from picogl.backend.gl.driver.capability import GLCapabilityDriver


class GLFog:
    """gl Fog"""
    FOG = GL_FOG
    FOG_COLOR = GL_FOG_COLOR
    FOG_END = GL_FOG_END
    FOG_MODE = GL_FOG_MODE
    FOG_START = GL_FOG_START
    FOG_INDEX = GL_FOG_INDEX


def set_fog_state(
    fog_state: bool,
    fog_density_value: float,
    fog_start_value: float,
    fog_end_value: float,
) -> None:
    """
    set_fog_state

    :param fog_density_value: float
    :param fog_end_value: float
    :param fog_start_value: float
    :param fog_state: bool
    :return: None
    """
    if fog_start_value >= fog_end_value:
        fog_start_value = fog_end_value - 1
    fog_density_value = min(0.3, fog_density_value)
    if fog_state:
        GLCapabilityDriver.enable(GLFog.FOG)
        glFogfv(
            GLFog.FOG_COLOR,
            [
                fog_density_value,
                fog_density_value,
                fog_density_value,
                fog_density_value,
            ],
        )
        glFogi(GLFog.FOG_MODE, GL_LINEAR)
        glFogf(GLFog.FOG_START, fog_start_value)
        glFogf(GLFogFOG_END, fog_end_value)
    else:
        GLCapabilityDriver.disable(GLFog.FOG)