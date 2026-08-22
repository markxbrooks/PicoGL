"""Fixed-function orbit camera for legacy GLUT renderers."""

from __future__ import annotations

from typing import Sequence

from molib.pdb.coordinate.coordinate import Coordinates
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.glu.lookat import glu_look_at, glu_look_at_coords
from picogl.core.protocol.applicable import Applicable
from picogl.ui.backend.glut.mouse import RotationInteraction


class LegacyCamera(Applicable):
    """Eye-space orbit camera: look-at distance plus drag rotation."""

    def __init__(self, distance: float = 5.0) -> None:
        self.distance = float(distance)
        self.rotation = RotationInteraction()

    def apply(self) -> None:
        """Install modelview look-at and current orbit rotation."""
        gl_load_identity()
        eye = Coordinates(x=0.0, y=0.0, z=self.distance)
        center = Coordinates.origin()
        up = Coordinates(x=0.0, y=1.0, z=0.0)
        glu_look_at_coords(eye, center, up)
        gl_rotate_f(self.rotation.x, 1.0, 0.0, 0.0)
        gl_rotate_f(self.rotation.y, 0.0, 1.0, 0.0)
