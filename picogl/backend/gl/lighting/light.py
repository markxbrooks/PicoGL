"""Fixed-function light value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from picogl.backend.gl.api.light import gl_light_fv
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLLight, GLLightParameter
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


class GLLightingMode(Enum):
    """GL Lighting mode"""

    EYE_SPACE = 0
    CAMERA_FIXED = 1
    CAMERA_ORIGIN = 2
    WORLD_SPACE = 3


rgba_tuple = tuple[float, float, float, float]


@dataclass(frozen=True)
class LightSource:
    """Light Source

    Accidental construction of ``LightSource()`` produces a
    soft white directional light suitable for general rendering.
    """

    position: Vec4 = field(default_factory=lambda: Vec4(10.0, 10.0, 10.0, 1.0))
    ambient: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.18, 0.18, 0.18, 1.0)
    )
    diffuse: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.55, 0.55, 0.55, 1.0)
    )
    specular: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.2, 0.2, 0.2, 1.0)
    )

    @classmethod
    def directional(
            cls,
            direction: Vec3,
    ) -> "LightSource":

    @classmethod
    def from_raw(
            cls,
            position: rgba_tuple,
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
        gl_light_fv(light, GLLightParameter.POSITION, self.position)
        gl_light_fv(light, GLLightParameter.AMBIENT, self.ambient)
        gl_light_fv(light, GLLightParameter.DIFFUSE, self.diffuse)
        gl_light_fv(light, GLLightParameter.SPECULAR, self.specular)
