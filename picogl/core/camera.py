"""Shared camera defaults used by Qt, GLUT, and backend projection helpers."""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from pyglm import glm


@dataclass(frozen=True)
class ProjectionConfig:
    """Perspective projection parameters used by PicoGL camera helpers."""

    fovy: float = 45.0
    aspect: float = 1.0
    near: float = 1.0
    far: float = 1000.0

    def with_aspect(self, aspect: float) -> ProjectionConfig:
        """Return a copy with ``aspect`` set."""
        return replace(self, aspect=float(aspect))

    def with_size(self, width: float, height: float) -> ProjectionConfig:
        """Return a copy with aspect from ``width / max(height, 1)``."""
        return self.with_aspect(float(width) / float(max(height, 1)))

    def matrix(self, aspect: float | None = None) -> glm.mat4:
        """Build a perspective projection matrix.

        If *aspect* is given, use it without mutating this config.
        """
        cfg = self if aspect is None else self.with_aspect(aspect)
        return glm.perspective(
            glm.radians(cfg.fovy),
            float(cfg.aspect),
            float(cfg.near),
            float(cfg.far),
        )


FOVY = ProjectionConfig().fovy


@dataclass
class CameraParameters:
    """Look-at parameters that build a view matrix.

    Example::

        camera = CameraParameters(eye=glm.vec3(4, 3, zoom_distance))
        view = camera.view_matrix()
    """

    eye: glm.vec3
    center: glm.vec3 = field(default_factory=lambda: glm.vec3(0, 0, 0))
    up: glm.vec3 = field(default_factory=lambda: glm.vec3(0, 1, 0))

    def view_matrix(self) -> glm.mat4:
        """Build the view matrix for this look-at triple."""
        return glm.lookAt(self.eye, self.center, self.up)

    @classmethod
    def tutorial(
        cls, distance: float = 3.0, *, z_sign: float = 1.0
    ) -> CameraParameters:
        """OpenGL-tutorial style eye at ``(4, 3, z_sign * distance)``."""
        return cls(eye=glm.vec3(4, 3, z_sign * distance))


@dataclass
class CameraConfig:
    """Bundled camera pose plus projection settings."""

    position: glm.vec3
    target: glm.vec3
    up: glm.vec3
    projection: ProjectionConfig = field(default_factory=ProjectionConfig)

    def camera_parameters(self) -> CameraParameters:
        """Look-at triple for this camera (ignores projection)."""
        return CameraParameters(eye=self.position, center=self.target, up=self.up)


DEFAULT_CAMERA_CONFIG = CameraConfig(
    position=glm.vec3(4, 3, 3),
    target=glm.vec3(0, 0, 0),
    up=glm.vec3(0, 1, 0),
    projection=ProjectionConfig(),
)
