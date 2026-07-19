"""
Provides a utility function for setting up lighting in a legacy OpenGL
rendering context.

This module configures a basic fixed-function light and material using
PicoGL value objects.

Functions:
- gl_legacy_lighting: Configures the lighting and material parameters
  for a default scene.

"""

from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace)
from picogl.backend.gl.lighting import LightSource, enable_light
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


DEFAULT_LEGACY_LIGHT = LightSource(
    position=Vec4(1.0, 1.0, 1.0, 0.0),
    ambient=RGBAColor(0.3, 0.3, 0.3, 1.0),
    diffuse=RGBAColor(0.8, 0.8, 0.8, 1.0),
    specular=RGBAColor(1.0, 1.0, 1.0, 1.0),
)

DEFAULT_LEGACY_MATERIAL = PhongMaterial(
    ambient=RGBAColor(0.2, 0.2, 0.2, 1.0),
    diffuse=RGBAColor(0.8, 0.8, 0.8, 1.0),
    specular=RGBAColor(1.0, 1.0, 1.0, 1.0),
    shininess=50.0,
)


def gl_legacy_lighting() -> None:
    """Install the default legacy light and material."""
    enable_light(GLFixedFunctionCapability.LIGHT0, DEFAULT_LEGACY_LIGHT)
    DEFAULT_LEGACY_MATERIAL.apply(GLMaterialFace.FRONT_AND_BACK)
