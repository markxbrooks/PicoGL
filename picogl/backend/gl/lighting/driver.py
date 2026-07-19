"""Upload fixed-function lights to OpenGL."""

from __future__ import annotations

from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.light import GLLightSource
from picogl.backend.gl.lighting.light import GLLighting
from picogl.backend.gl.state.fill import GLLightParameter


def apply_light(
    capability: GLFixedFunctionCapability,
    light: GLLighting,
) -> None:
    """Apply position and colour terms for a light source."""
    GLLightSource.lightf(
        capability,
        GLLightParameter.POSITION,
        light.position.to_tuple(),
    )
    GLLightSource.lightf(
        capability,
        GLLightParameter.AMBIENT,
        light.ambient.to_tuple(),
    )
    GLLightSource.lightf(
        capability,
        GLLightParameter.DIFFUSE,
        light.diffuse.to_tuple(),
    )
    GLLightSource.lightf(
        capability,
        GLLightParameter.SPECULAR,
        light.specular.to_tuple(),
    )


def enable_light(
    capability: GLFixedFunctionCapability, light: GLLighting | None = None
) -> None:
    """Enable a light capability and optionally apply its parameters."""
    GLCapabilityDriver.enable(capability)
    if light is not None:
        apply_light(capability, light)


def disable_light(capability: GLFixedFunctionCapability) -> None:
    """Disable a fixed-function light capability."""
    GLCapabilityDriver.disable(capability)
