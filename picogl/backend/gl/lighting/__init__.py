"""Fixed-function lighting value objects, presets, and drivers."""

from picogl.backend.gl.lighting.driver import apply_light, disable_light, enable_light
from picogl.backend.gl.lighting.light import GLLightingMode, LightSource
from picogl.backend.gl.lighting.presets import (
    CAMERA_FIXED_LIGHTING,
    CAMERA_ORIGIN_LIGHT,
    CAMERA_ORIGIN_LIGHTING,
    EYE_SPACE_LIGHTING,
    LEGACY_EYE_LIGHT,
    LIGHTING_PRESETS,
    SECONDARY_LIGHTS,
    WORLD_LIGHT,
    WORLD_SPACE_LIGHTING,
    set_secondary_lights,
)
from picogl.backend.gl.lighting.system import GLLightingSystem

__all__ = [
    "CAMERA_FIXED_LIGHTING",
    "CAMERA_ORIGIN_LIGHT",
    "CAMERA_ORIGIN_LIGHTING",
    "EYE_SPACE_LIGHTING",
    "LightSource",
    "GLLightingMode",
    "GLLightingSystem",
    "LEGACY_EYE_LIGHT",
    "LIGHTING_PRESETS",
    "SECONDARY_LIGHTS",
    "WORLD_LIGHT",
    "WORLD_SPACE_LIGHTING",
    "apply_light",
    "disable_light",
    "enable_light",
    "set_secondary_lights",
]
