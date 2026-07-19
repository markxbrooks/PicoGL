"""
Setup lighting (compatibility shim).

Prefer ``picogl.backend.gl.lighting`` for new code.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from picogl.backend.gl.lighting import (EYE_SPACE_LIGHTING, GLLighting,
                                        GLLightingMode, LIGHTING_PRESETS,
                                        apply_light, disable_light,
                                        enable_light, set_secondary_lights)
from picogl.core.rgbcolor import RGBAColor
from picogl.gpu.buffers.glframe import GLFramebuffer

if TYPE_CHECKING:
    from picogl.backend.gl.backend import GLBackend

__all__ = [
    "GLLighting",
    "GLLightingMode",
    "apply_light",
    "disable_light",
    "enable_light",
    "set_background_color",
    "set_second_light_state",
    "setup_lighting",
    "setup_lighting_mode_zero",
]


def set_second_light_state(second_light_state: bool) -> None:
    """Enable or disable secondary fill lights."""
    set_secondary_lights(second_light_state)


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
    LIGHTING_PRESETS[mode].apply()


def setup_lighting_mode_zero(backend: GLBackend) -> None:
    """Install the eye-space LIGHT0 setup used by legacy GL init."""
    del backend  # reserved for future backend-aware lighting
    EYE_SPACE_LIGHTING.apply()
