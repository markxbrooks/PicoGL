from __future__ import annotations

from dataclasses import dataclass, field

from picogl.backend.gl.enums.legacy.scale import gl_rotatef, gl_scalef, gl_translate_f


class GLTranslation:
    """Translation Parameters"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def apply(self):
        gl_translate_f(self.x, self.y, self.z)

    def _apply_zoom(self, value: float = 0.01):
        gl_translate_f(self.translation.x, self.translation.y, value)


@dataclass
class GLZoom:
    """Zoom parameters."""

    # translation: GLTranslation = None
    value: float = -5.0

    """def apply(self):
        self.apply_translation_and_zoom(self.translation, self.value)"""

    def apply_translation_and_zoom(self, translation, zoom):
        gl_translate_f(translation.x, translation.y, zoom)

    def rescale(self):
        gl_scalef(self.value, self.value, self.value)


@dataclass
class GLRotation:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def apply(self):
        gl_rotatef(self.x, 1.0, 0.0, 0.0)
        gl_rotatef(self.y, 0.0, 1.0, 0.0)
        gl_rotatef(self.z, 0.0, 0.0, 1.0)


@dataclass
class CameraPerspective:
    """
    Represents parameters required to define a camera perspective.

    This class provides default values for the far clipping plane, near clipping
    plane, and field of view in the y-direction (fovy) for a perspective camera.
    These parameters can be used to set up a perspective projection for 3D rendering.
    """

    FAR: float = 100.0
    NEAR: float = 0.1
    FOVY: float = 45.0


@dataclass
class LegacyGLViewTransform:
    """Encapsulates legacy OpenGL view rotation, translation, and zoom."""

    rotation: GLRotation = field(default_factory=GLRotation)
    translation: GLTranslation = field(default_factory=GLTranslation)
    zoom: GLZoom = field(default_factory=lambda: GLZoom(value=1.0))

    @property
    def rotation_x(self) -> float:
        return self.rotation.x

    @rotation_x.setter
    def rotation_x(self, value: float) -> None:
        self.rotation.x = value

    @property
    def rotation_y(self) -> float:
        return self.rotation.y

    @rotation_y.setter
    def rotation_y(self, value: float) -> None:
        self.rotation.y = value

    @property
    def translation_x(self) -> float:
        return self.translation.x

    @translation_x.setter
    def translation_x(self, value: float) -> None:
        self.translation.x = value

    @property
    def translation_y(self) -> float:
        return self.translation.y

    @translation_y.setter
    def translation_y(self, value: float) -> None:
        self.translation.y = value

    def apply(self) -> None:
        """Apply the view transform using the legacy OpenGL matrix stack."""
        self.translation.apply()
        self.rotation.apply()

    def reset(self) -> None:
        """Reset view transformation to defaults."""
        self.rotation = GLRotation()
        self.translation = GLTranslation()
        self.zoom = GLZoom(value=1.0)
