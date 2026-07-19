"""Fixed-function light value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


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
