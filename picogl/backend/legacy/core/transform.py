"""
This module provides functionality for applying transformations including
translation, rotation, and scaling to a specific graphical context using OpenGL
legacy API methods.

The Transform class encapsulates a set of transformation properties which
can be applied sequentially in the order of translation, rotation, and scaling.
"""

from dataclasses import dataclass, field

from molib.pdb.coordinate.coordinate import Coordinates

from picogl.backend.gl.api.legacy.rotate import gl_rotate_f
from picogl.backend.gl.enums.legacy.scale import gl_scalef, gl_translate_f


@dataclass
class Transform:
    """Transform"""

    translation: Coordinates = field(default_factory=lambda: Coordinates(0.0, 0.0, 0.0))
    rotation: Coordinates = field(default_factory=lambda: Coordinates(0.0, 0.0, 0.0))
    scale: Coordinates = field(default_factory=lambda: Coordinates(1.0, 1.0, 1.0))

    def apply(self):
        gl_translate_f(
            self.translation.x,
            self.translation.y,
            self.translation.z,
        )

        gl_rotate_f(
            self.rotation.x,
            1.0,
            0.0,
            0.0,
        )

        gl_rotate_f(
            self.rotation.y,
            0.0,
            1.0,
            0.0,
        )

        gl_scalef(
            self.scale.x,
            self.scale.y,
            self.scale.z,
        )
