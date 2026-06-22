"""
Setup lighting
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_UNPACK_ALIGNMENT, glLoadIdentity,
                                          glMaterialf, glMatrixMode,
                                          glPixelStorei, glPopMatrix,
                                          glPushMatrix)
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.light import GLLightSource
from picogl.gpu.buffers.glframe import GLFramebuffer
from picogl.state.fill import GLFace, GLLightParameter


def set_second_light_state(second_light_state: bool) -> None:
    """
    set_second_light_state

    :param second_light_state: bool Whether the second light is on or off
    :return: None

    Second light
    """
    if second_light_state:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT1)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT1,
            GLLightParameter.POSITION,
            [-10.0, -10.0, -10.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT1,
            GLLightParameter.DIFFUSE,
            [0.5, 0.5, 0.5, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT1,
            GLLightParameter.SPECULAR,
            [0.3, 0.3, 0.3, 1.0],
        )
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT2)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT2,
            GLLightParameter.POSITION,
            [90.0, 90.0, 90.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT2,
            GLLightParameter.DIFFUSE,
            [0.5, 0.5, 0.5, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT2,
            GLLightParameter.SPECULAR,
            [0.3, 0.3, 0.3, 1.0],
        )
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT3)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT3,
            GLLightParameter.POSITION,
            [-90.0, -90.0, -90.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT3,
            GLLightParameter.DIFFUSE,
            [0.5, 0.5, 0.5, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT3,
            GLLightParameter.SPECULAR,
            [0.3, 0.3, 0.3, 1.0],
        )
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT4)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT4,
            GLLightParameter.POSITION,
            [270.0, 270.0, 270.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT4,
            GLLightParameter.DIFFUSE,
            [0.5, 0.5, 0.5, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT4,
            GLLightParameter.SPECULAR,
            [0.3, 0.3, 0.3, 1.0],
        )
    else:
        GLCapabilityDriver.disable(GLFixedFunctionCapability.LIGHT1)


def set_background_color(show_white_background: bool) -> None:
    """
    set_background_color

    :param show_white_background: bool
    :return: None
    Choose bg color_array
    """
    if show_white_background:
        color = (1.0, 1.0, 1.0, 1.0)  # White background
    else:
        color = (0.0, 0.0, 0.0, 1.0)
    buffer = GLFramebuffer()
    buffer.clear(color=color)


def setup_lighting(mode: int = 0) -> None:
    """
    setup_lighting

    :param mode: int lighting gl_mode
    :return: None
    """
    current_shininess = 1.0
    if mode == 0:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)
        # GLCapabilityDriver.enable(GL_COLOR_MATERIAL)
        # Set up light position_array (in eye space)
        light_pos = [10.0, 10.0, 10.0, 1.0]  # positional black light
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0, GLLightParameter.POSITION, light_pos
        )
        # Set light color_array
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.2, 0.2, 0.2, 1.0],
        )
        glMaterialf(
            GLFace.FRONT_AND_BACK, GLLightParameter.SHININESS, 128.0 * current_shininess
        )
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    if mode == 2:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)
        # Set up light position_array (in eye space)
        light_pos = [0.0, 0.0, 0.0, 1.0]  # positional light
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0, GLLightParameter.POSITION, light_pos
        )
        # Set light color_array
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.2, 0.2, 0.2, 1.0],
        )
    elif mode == 1:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)

        glMatrixMode(GLLegacyMatrixMode.MODELVIEW)
        glPushMatrix()
        glLoadIdentity()  # reset modelview matrix

        # Set light position_array (camera-relative)
        light_pos = [10.0, 10.0, 10.0, 1.0]
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0, GLLightParameter.POSITION, light_pos
        )

        glPopMatrix()

        # Set light properties (these are not affected by the matrix)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.2, 0.2, 0.2, 1.0],
        )
    elif mode == 3:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)
        # Set light properties (independent of matrix)
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [1.0, 1.0, 1.0, 1.0],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.2, 0.2, 0.2, 1.0],
        )

        # Call this *after* your model_matrix/view transforms (e.g., after gl_update_camera_matrix)
        light_pos = [
            10.0,
            10.0,
            10.0,
            1.0,
        ]  # Positional light, relative to object/world
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0, GLLightParameter.POSITION, light_pos
        )


def setup_lighting_mode_zero(backend: "GLBackend"):
    setup_lighting(mode=0)
