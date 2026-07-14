"""
Setup lighting
"""
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_UNPACK_ALIGNMENT,
                                          )

from backend.gl.api.legacy.pixel_store import gl_pixel_store_i
from picogl.backend.gl.api.legacy.matrix import gl_matrix_mode
from picogl.backend.gl.api.material import gl_material_f
from picogl.core.rgbcolor import RGBAColor
from picogl.backend.gl.enums.legacy.scale import gl_push_matrix, gl_pop_matrix
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.light import GLLightSource
from picogl.backend.gl.state.fill import GLFace, GLLightParameter
from picogl.gpu.buffers.glframe import GLFramebuffer

class GLLightingMode(Enum):
    """GL Lighting mode"""
    EYE_SPACE = 0
    CAMERA_FIXED = 1
    CAMERA_ORIGIN = 2
    WORLD_SPACE = 3


@dataclass(frozen=True)
class GLLight:
    """GL Light"""
    position: Sequence[float] = (10.0, 10.0, 10.0, 1.0)
    ambient: Sequence[float] = (0.2, 0.2, 0.2, 1.0)
    diffuse: Sequence[float] = (1.0, 1.0, 1.0, 1.0)
    specular: Sequence[float] = (1.0, 1.0, 1.0, 1.0)


def apply_light(
    capability: GLFixedFunctionCapability,
    light: GLLight,
) -> None:
    GLLightSource.lightf(
        capability,
        GLLightParameter.POSITION,
        light.position,
    )

    GLLightSource.lightf(
        capability,
        GLLightParameter.AMBIENT,
        light.ambient,
    )

    GLLightSource.lightf(
        capability,
        GLLightParameter.DIFFUSE,
        light.diffuse,
    )

    GLLightSource.lightf(
        capability,
        GLLightParameter.SPECULAR,
        light.specular,
    )

def set_second_light_state(second_light_state: bool) -> None:
    """
    set_second_light_state

    :param second_light_state: bool Whether the second light is on or off
    :return: None

    Second light
    """
    if second_light_state:
        light1 = GLLight(position=[-10.0, -10.0, -10.0, 1.0],
                         diffuse=[0.5, 0.5, 0.5, 1.0],
                         specular=[0.3, 0.3, 0.3, 1.0],
                         ambient=[0.3, 0.3, 0.3, 1.0])
        light2 = GLLight(position=[90.0, 90.0, 90.0, 1.0],
                         diffuse=[0.5, 0.5, 0.5, 1.0],
                         specular=[0.3, 0.3, 0.3, 1.0],
                         ambient=[0.3, 0.3, 0.3, 1.0])
        light3 = GLLight(position=[-90.0, -90.0, -90.0, 1.0],
                         diffuse=[0.5, 0.5, 0.5, 1.0],
                         specular=[0.3, 0.3, 0.3, 1.0],
                         ambient=[0.3, 0.3, 0.3, 1.0])
        light4 = GLLight(position=[270.0, 270.0, 270.0, 1.0],
                         diffuse=[0.5, 0.5, 0.5, 1.0],
                         specular=[0.3, 0.3, 0.3, 1.0],
                         ambient=[0.3, 0.3, 0.3, 1.0])
        lights = {GLFixedFunctionCapability.LIGHT1: light1,
                  GLFixedFunctionCapability.LIGHT2: light2,
                  GLFixedFunctionCapability.LIGHT3: light3,
                  GLFixedFunctionCapability.LIGHT4: light4}
        for capability, light in lights.items():
            enable_light(capability=capability, light=light1)

    else:
        GLCapabilityDriver.disable(GLFixedFunctionCapability.LIGHT1)


def enable_light(capability: GLFixedFunctionCapability, light: GLLight = None) -> None:
    """enable light"""
    GLCapabilityDriver.enable(capability)
    if light is not None:
        apply_light(capability, light)


def set_background_color(show_white_background: bool) -> None:
    """
    set_background_color

    :param show_white_background: bool
    :return: None
    Choose bg color_array
    """
    if show_white_background:
        color = RGBAColor(1.0, 1.0, 1.0, 1.0)  # White background
    else:
        color = RGBAColor(0.0, 0.0, 0.0, 1.0)
    buffer = GLFramebuffer()
    buffer.clear(color=color.tuple)


def setup_lighting(mode: GLLightingMode = GLLightingMode.EYE_SPACE) -> None:
    """
    setup_lighting

    :param mode: int lighting gl_mode
    :return: None
    """
    current_shininess = 1.0
    if mode == GLLightingMode.EYE_SPACE:
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
            [0.2, 0.2, 0.2, 0.2],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            [0.3, 0.3, 0.3, 0.2],
        )
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            [0.2, 0.2, 0.2, 0.2],
        )
        gl_material_f(
            GLFace.FRONT_AND_BACK, GLLightParameter.SHININESS, 128.0 * current_shininess
        )
        gl_pixel_store_i(GL_UNPACK_ALIGNMENT, 1)
    if mode == GLLightingMode.CAMERA_ORIGIN:
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
    elif mode == GLLightingMode.WORLD_SPACE:
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)

        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
        gl_push_matrix()
        gl_load_identity()  # reset modelview matrix

        # Set light position_array (camera-relative)
        light_pos = [10.0, 10.0, 10.0, 1.0]
        GLLightSource.lightf(
            GLFixedFunctionCapability.LIGHT0, GLLightParameter.POSITION, light_pos
        )

        gl_pop_matrix()

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

`


def setup_lighting_mode_zero(backend: "GLBackend"):
    setup_lighting(mode=GLLightingMode.EYE_SPACE)
