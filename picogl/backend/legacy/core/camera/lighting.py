"""
Setup lighting
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_LIGHT_MODEL_AMBIENT,
    GL_UNPACK_ALIGNMENT
)

from picogl.backend.gl.api.legacy.pixel_store import gl_pixel_store_i
from picogl.backend.gl.api.light.model import gl_light_model_fv
from picogl.backend.gl.api.material import gl_material_f
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.legacy.matrix import gl_pushed_matrix
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.light import GLLightSource
from picogl.backend.gl.state.fill import GLFace, GLLightParameter
from picogl.core.rgbcolor import RGBAColor
from picogl.gpu.buffers.glframe import GLFramebuffer

if TYPE_CHECKING:
    from picogl.backend.gl.backend import GLBackend


class GLLightingMode(Enum):
    """GL Lighting mode"""

    EYE_SPACE = 0
    CAMERA_FIXED = 1
    CAMERA_ORIGIN = 2
    WORLD_SPACE = 3


@dataclass(frozen=True)
class GLLight:
    """GL Light

    Defaults stay muted (near modern shader ambient ~0.18) so accidental use of
    ``GLLight()`` does not install a full-bright OpenGL LIGHT0.
    """

    position: Sequence[float] = (10.0, 10.0, 10.0, 1.0)
    ambient: Sequence[float] = (0.18, 0.18, 0.18, 1.0)
    diffuse: Sequence[float] = (0.55, 0.55, 0.55, 1.0)
    specular: Sequence[float] = (0.2, 0.2, 0.2, 1.0)


# Dim eye-space LIGHT0 used by legacy molecule viewers (ElMo paintGL).
_EYE_SPACE_LIGHT0 = GLLight(
    position=(10.0, 10.0, 10.0, 1.0),
    ambient=(0.15, 0.15, 0.15, 1.0),
    diffuse=(0.35, 0.35, 0.35, 1.0),
    specular=(0.12, 0.12, 0.12, 1.0),
)

_CAMERA_ORIGIN_LIGHT0 = GLLight(
    position=(0.0, 0.0, 0.0, 1.0),
    ambient=(0.18, 0.18, 0.18, 1.0),
    diffuse=(0.7, 0.7, 0.7, 1.0),
    specular=(0.25, 0.25, 0.25, 1.0),
)

_WORLD_OR_FIXED_LIGHT0 = GLLight(
    position=(10.0, 10.0, 10.0, 1.0),
    ambient=(0.18, 0.18, 0.18, 1.0),
    diffuse=(0.7, 0.7, 0.7, 1.0),
    specular=(0.25, 0.25, 0.25, 1.0),
)


def apply_light(
    capability: GLFixedFunctionCapability,
    light: GLLight,
) -> None:
    """Apply position and material terms for an enabled light source."""
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
    secondary = (
        GLFixedFunctionCapability.LIGHT1,
        GLFixedFunctionCapability.LIGHT2,
        GLFixedFunctionCapability.LIGHT3,
        GLFixedFunctionCapability.LIGHT4,
    )
    if second_light_state:
        # Keep fill lights soft so they don't wash out COLOUR_MATERIAL.
        soft = dict(
            diffuse=(0.25, 0.25, 0.25, 1.0),
            specular=(0.1, 0.1, 0.1, 1.0),
            ambient=(0.08, 0.08, 0.08, 1.0),
        )
        lights = {
            GLFixedFunctionCapability.LIGHT1: GLLight(
                position=(-10.0, -10.0, -10.0, 1.0), **soft
            ),
            GLFixedFunctionCapability.LIGHT2: GLLight(
                position=(90.0, 90.0, 90.0, 1.0), **soft
            ),
            GLFixedFunctionCapability.LIGHT3: GLLight(
                position=(-90.0, -90.0, -90.0, 1.0), **soft
            ),
            GLFixedFunctionCapability.LIGHT4: GLLight(
                position=(270.0, 270.0, 270.0, 1.0), **soft
            ),
        }
        for capability, light in lights.items():
            enable_light(capability=capability, light=light)
    else:
        for capability in secondary:
            GLCapabilityDriver.disable(capability)


def enable_light(
    capability: GLFixedFunctionCapability, light: GLLight | None = None
) -> None:
    """Enable a light capability and optionally apply its parameters."""
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

    :param mode: lighting mode
    :return: None
    """
    current_shininess = 1.0
    GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
    # Default OpenGL light-model ambient (0.2) adds a flat wash under COLOR_MATERIAL.
    gl_light_model_fv(GL_LIGHT_MODEL_AMBIENT, (0.12, 0.12, 0.12, 1.0))

    if mode == GLLightingMode.EYE_SPACE:
        enable_light(GLFixedFunctionCapability.LIGHT0, _EYE_SPACE_LIGHT0)
        gl_material_f(
            GLFace.FRONT_AND_BACK, GLLightParameter.SHININESS, 32.0 * current_shininess
        )
        gl_pixel_store_i(GL_UNPACK_ALIGNMENT, 1)

    elif mode == GLLightingMode.CAMERA_ORIGIN:
        enable_light(GLFixedFunctionCapability.LIGHT0, _CAMERA_ORIGIN_LIGHT0)

    elif mode == GLLightingMode.WORLD_SPACE:
        # Set light position in camera space by clearing the modelview first.
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
        with gl_pushed_matrix():
            gl_load_identity()
            enable_light(GLFixedFunctionCapability.LIGHT0, _WORLD_OR_FIXED_LIGHT0)

    elif mode == GLLightingMode.CAMERA_FIXED:
        # Call after model/view transforms (e.g. after gl_update_camera_matrix).
        enable_light(GLFixedFunctionCapability.LIGHT0, _WORLD_OR_FIXED_LIGHT0)


def setup_lighting_mode_zero(backend: GLBackend) -> None:
    """Install the eye-space LIGHT0 setup used by legacy GL init."""
    del backend  # reserved for future backend-aware lighting
    setup_lighting(mode=GLLightingMode.EYE_SPACE)
