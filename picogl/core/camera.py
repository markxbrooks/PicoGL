"""Shared camera defaults used by Qt, GLUT, and backend projection helpers."""
from dataclasses import dataclass, field, replace

from pyglm import glm


@dataclass(frozen=True)
class ProjectionConfig:
    """Perspective frustum used by PicoGL camera helpers."""

    fovy: float = 45.0
    aspect: float = 1.0
    near: float = 1.0
    far: float = 1000.0

    def with_aspect(self, aspect: float) -> "ProjectionConfig":
        """Return a copy with ``aspect`` set."""
        return replace(self, aspect=float(aspect))

    def with_size(self, width: float, height: float) -> "ProjectionConfig":
        """Return a copy with aspect from ``width / max(height, 1)``."""
        return self.with_aspect(float(width) / float(max(height, 1)))


FOVY = ProjectionConfig().fovy


@dataclass
class CameraConfig:
    """Camera Config"""

    position: glm.vec3
    target: glm.vec3
    up: glm.vec3
    projection: ProjectionConfig = field(default_factory=ProjectionConfig)


DEFAULT_CAMERA_CONFIG = CameraConfig(
    position=glm.vec3(4, 3, 3),
    target=glm.vec3(0, 0, 0),
    up=glm.vec3(0, 1, 0),
    projection=ProjectionConfig(),
)
