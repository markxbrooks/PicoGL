"""
Provides a utility function for setting up lighting in a legacy OpenGL
rendering context.

This module configures a basic fixed-function light and material using
PicoGL value objects.

Functions:
- gl_legacy_lighting: Configures the lighting and material parameters
  for a default scene.

"""

from __future__ import annotations

from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import (
    gl_disable_capability_list,
    gl_enable_capability_list,
)
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from picogl.backend.gl.lighting import LightSource, enable_light
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode, GLLight
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


class GLFixedFunctionLightingModel:
    """GLLightingModel"""

    LIGHT = LightSource(
        position=Vec4(1.0, 1.0, 1.0, 0.0),
        ambient=RGBAColor(0.4, 0.4, 0.4, 1.0),
        diffuse=RGBAColor(0.6, 0.6, 0.6, 1.0),
        specular=RGBAColor(0.2, 0.2, 0.2, 1.0),
    )
    MATERIAL = PhongMaterial(
        ambient=RGBAColor(0.3, 0.3, 0.3, 1.0),
        diffuse=RGBAColor(0.7, 0.7, 0.7, 1.0),
        specular=RGBAColor(0.1, 0.1, 0.1, 1.0),
        shininess=50.0,
    )
    CAPABILITIES = [
        GLFixedFunctionCapability.LIGHTING,
        GLFixedFunctionCapability.LIGHT0,
        GLCapability.COLOR_MATERIAL,
    ]

    def apply(self) -> None:
        """Enable or disable fixed-function lighting for this frame."""
        self.enable()
        self.setup_color_materials()
        self.setup_light_source()
        self.setup_materials()

    def setup_color_materials(self):
        """setup color materials"""
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )

    def setup_materials(self):
        """setup materials"""
        self.MATERIAL.apply(GLMaterialFace.FRONT_AND_BACK)

    def setup_light_source(self):
        """setup light source"""
        self.LIGHT.apply(GLLight.LIGHT0)

    def enable(self):
        """enable"""
        gl_enable_capability_list(self.CAPABILITIES)

    def disable(self):
        """disable"""
        gl_disable_capability_list(self.CAPABILITIES)
