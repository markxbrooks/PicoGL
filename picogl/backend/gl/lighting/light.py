"""Fixed-function light value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from molib.pdb.materials import Vec3
from picogl.backend.gl.api.light import gl_light_fv
from picogl.backend.gl.state.fill import GLLightParameter
from picogl.core.data_type import rgba_tuple, vec4_tuple
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


class GLLightingMode(Enum):
    """GL Lighting mode"""

    EYE_SPACE = 0
    CAMERA_FIXED = 1
    CAMERA_ORIGIN = 2
    WORLD_SPACE = 3


@dataclass(frozen=True)
class LightSource:
    """Light Source

    Accidental construction of ``LightSource()`` produces a
    soft white directional light suitable for general rendering.
    """

    position: Vec4 = field(default_factory=lambda: Vec4(10.0, 10.0, 10.0, 1.0))
    ambient: RGBAColor = field(default_factory=lambda: RGBAColor(0.18, 0.18, 0.18, 1.0))
    diffuse: RGBAColor = field(default_factory=lambda: RGBAColor(0.55, 0.55, 0.55, 1.0))
    specular: RGBAColor = field(default_factory=lambda: RGBAColor(0.2, 0.2, 0.2, 1.0))

    @classmethod
    def directional(
        cls,
        direction: Vec3,
    ) -> "LightSource":
        return cls(
            position=Vec4(direction, 0.0),
            ambient=RGBAColor(0.0, 0.0, 0.0, 1.0),
            diffuse=RGBAColor(1.0, 1.0, 1.0, 1.0),
            specular=RGBAColor(0.0, 0.0, 0.0, 1.0),
        )

    @classmethod
    def from_raw(
        cls,
        position: vec4_tuple,
        ambient: rgba_tuple,
        diffuse: rgba_tuple,
        specular: rgba_tuple,
    ) -> "LightSource":
        return cls(
            position=Vec4(*position),
            ambient=RGBAColor(*ambient),
            diffuse=RGBAColor(*diffuse),
            specular=RGBAColor(*specular),
        )

    def apply(self, light):
        """apply the lighting"""
        gl_light_fv(light, GLLightParameter.POSITION, self.position.to_tuple())
        gl_light_fv(light, GLLightParameter.AMBIENT, self.ambient.to_tuple())
        gl_light_fv(light, GLLightParameter.DIFFUSE, self.diffuse.to_tuple())
        gl_light_fv(light, GLLightParameter.SPECULAR, self.specular.to_tuple())
