from dataclasses import dataclass, field

from backend.gl.enums.legacy.scale import gl_translate_f
from core.vec3 import Vec3
from core.zoom.scale import gl_scale_by_zoom
from examples.cube_with_controls import Axes, gl_rotate_axes
from molib.pdb.coordinate.coordinate import Coordinates


@dataclass(slots=True)
class GLViewTransform:
    """View Transform"""

    zoom: float
    rotation: Vec3
    scale: float = 20.0
    origin: Coordinates = field(default_factory=lambda: Coordinates(0.5, 0.5, 0.5))
    axes: Axes = field(default_factory=lambda: Axes())

    def apply(self) -> None:
        print(self.rotation)
        gl_translate_f(0.0, 0.0, self.zoom)
        gl_scale_by_zoom(self.scale)
        gl_rotate_axes(self.rotation, self.axes)
        gl_translate_f(-self.origin.x, -self.origin.y, -self.origin.z)
