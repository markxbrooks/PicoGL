"""Owned fixed-function lighting configuration."""

from __future__ import annotations

from dataclasses import dataclass, field

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_UNPACK_ALIGNMENT
from picogl.backend.gl.api.legacy.matrix import gl_pushed_matrix
from picogl.backend.gl.api.legacy.pixel_store import gl_pixel_store_i
from picogl.backend.gl.api.light.model import gl_light_model_fv
from picogl.backend.gl.api.material import gl_material_f
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.enums.light import GLLightModel
from picogl.backend.gl.lighting.driver import enable_light
from picogl.backend.gl.lighting.light import GLLightingMode, LightSource
from picogl.backend.gl.state.fill import GLFace, GLLightParameter
from picogl.core.rgbcolor import RGBAColor


@dataclass
class GLLightingSystem:
    """Configuration for fixed-function lighting state."""

    mode: GLLightingMode = GLLightingMode.EYE_SPACE
    ambient: RGBAColor = field(default_factory=lambda: RGBAColor(0.12, 0.12, 0.12, 1.0))
    lights: dict[GLFixedFunctionCapability, LightSource] = field(default_factory=dict)
    material_shininess: float | None = None
    set_unpack_alignment: bool = False

    def apply(self) -> None:
        """Install this lighting configuration into the current GL context."""
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        gl_light_model_fv(GLLightModel.AMBIENT, self.ambient.to_tuple())

        if self.mode == GLLightingMode.WORLD_SPACE:
            gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
            with gl_pushed_matrix():
                gl_load_identity()
                self._enable_lights()
            gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        else:
            self._enable_lights()

        if self.material_shininess is not None:
            gl_material_f(
                GLFace.FRONT_AND_BACK,
                GLLightParameter.SHININESS,
                float(self.material_shininess),
            )
        if self.set_unpack_alignment:
            gl_pixel_store_i(GL_UNPACK_ALIGNMENT, 1)

    def _enable_lights(self) -> None:
        for capability, light in self.lights.items():
            enable_light(capability, light)
