"""Named fixed-function light and lighting-system presets."""

from __future__ import annotations

from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.lighting.driver import disable_light, enable_light
from picogl.backend.gl.lighting.light import GLLight, GLLightingMode
from picogl.backend.gl.lighting.system import GLLightingSystem
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4

# Dim eye-space LIGHT0 used by legacy molecule viewers (ElMo paintGL).
LEGACY_EYE_LIGHT = GLLight(
    position=Vec4(10.0, 10.0, 10.0, 1.0),
    ambient=RGBAColor(0.15, 0.15, 0.15, 1.0),
    diffuse=RGBAColor(0.35, 0.35, 0.35, 1.0),
    specular=RGBAColor(0.12, 0.12, 0.12, 1.0),
)

CAMERA_ORIGIN_LIGHT = GLLight(
    position=Vec4(0.0, 0.0, 0.0, 1.0),
    ambient=RGBAColor(0.18, 0.18, 0.18, 1.0),
    diffuse=RGBAColor(0.7, 0.7, 0.7, 1.0),
    specular=RGBAColor(0.25, 0.25, 0.25, 1.0),
)

WORLD_LIGHT = GLLight(
    position=Vec4(10.0, 10.0, 10.0, 1.0),
    ambient=RGBAColor(0.18, 0.18, 0.18, 1.0),
    diffuse=RGBAColor(0.7, 0.7, 0.7, 1.0),
    specular=RGBAColor(0.25, 0.25, 0.25, 1.0),
)

# Soft fill lights so they don't wash out COLOR_MATERIAL.
_SOFT = dict(
    diffuse=RGBAColor(0.25, 0.25, 0.25, 1.0),
    specular=RGBAColor(0.1, 0.1, 0.1, 1.0),
    ambient=RGBAColor(0.08, 0.08, 0.08, 1.0),
)

SECONDARY_LIGHTS: dict[GLFixedFunctionCapability, GLLight] = {
    GLFixedFunctionCapability.LIGHT1: GLLight(
        position=Vec4(-10.0, -10.0, -10.0, 1.0), **_SOFT
    ),
    GLFixedFunctionCapability.LIGHT2: GLLight(
        position=Vec4(90.0, 90.0, 90.0, 1.0), **_SOFT
    ),
    GLFixedFunctionCapability.LIGHT3: GLLight(
        position=Vec4(-90.0, -90.0, -90.0, 1.0), **_SOFT
    ),
    GLFixedFunctionCapability.LIGHT4: GLLight(
        position=Vec4(270.0, 270.0, 270.0, 1.0), **_SOFT
    ),
}

EYE_SPACE_LIGHTING = GLLightingSystem(
    mode=GLLightingMode.EYE_SPACE,
    lights={GLFixedFunctionCapability.LIGHT0: LEGACY_EYE_LIGHT},
    material_shininess=32.0,
    set_unpack_alignment=True,
)

CAMERA_ORIGIN_LIGHTING = GLLightingSystem(
    mode=GLLightingMode.CAMERA_ORIGIN,
    lights={GLFixedFunctionCapability.LIGHT0: CAMERA_ORIGIN_LIGHT},
)

WORLD_SPACE_LIGHTING = GLLightingSystem(
    mode=GLLightingMode.WORLD_SPACE,
    lights={GLFixedFunctionCapability.LIGHT0: WORLD_LIGHT},
)

CAMERA_FIXED_LIGHTING = GLLightingSystem(
    mode=GLLightingMode.CAMERA_FIXED,
    lights={GLFixedFunctionCapability.LIGHT0: WORLD_LIGHT},
)

LIGHTING_PRESETS: dict[GLLightingMode, GLLightingSystem] = {
    GLLightingMode.EYE_SPACE: EYE_SPACE_LIGHTING,
    GLLightingMode.CAMERA_ORIGIN: CAMERA_ORIGIN_LIGHTING,
    GLLightingMode.WORLD_SPACE: WORLD_SPACE_LIGHTING,
    GLLightingMode.CAMERA_FIXED: CAMERA_FIXED_LIGHTING,
}


def set_secondary_lights(enabled: bool) -> None:
    """Enable or disable the soft secondary fill lights."""
    if enabled:
        for capability, light in SECONDARY_LIGHTS.items():
            enable_light(capability, light)
    else:
        for capability in SECONDARY_LIGHTS:
            disable_light(capability)
