"""Base GLUT fixed-function renderer: lifecycle, camera, viewport, projection."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod

# Before any OpenGL import: GLX under Wayland, Apple GLUT on macOS.
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401

from picogl.backend.gl.api.clear import gl_clear
from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.glut import (
    GLUTDisplayMode,
    GLUTMouseButton,
    GLUTMouseState,
    glut_create_window,
    glut_display_func,
    glut_idle_func,
    glut_init,
    glut_init_display_mode,
    glut_init_window_size,
    glut_keyboard_func,
    glut_main_loop,
    glut_motion_func,
    glut_mouse_func,
    glut_post_redisplay,
    glut_reshape_func,
    glut_swap_buffers,
)
from picogl.backend.legacy.core.camera.legacy_camera import LegacyCamera
from picogl.backend.legacy.core.camera.projection_state import GLUProjectionState
from picogl.backend.state import GLViewport
from picogl.core.camera import ProjectionConfig
from picogl.core.rgbcolor import RGBAColor


class LegacyRenderer(ABC):
    """Base GLUT fixed-function renderer: lifecycle, camera, viewport, projection."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy Renderer",
    ) -> None:
        self.width = width
        self.height = height
        self.title = title

        self.viewport = GLViewport(width=width, height=height)
        self.projection_config = ProjectionConfig(near=0.1, far=100.0)
        self.projection = GLUProjectionState()
        self.camera = LegacyCamera(distance=5.0)

    def init_glut(self) -> None:
        """Initialize GLUT window and callbacks."""
        glut_init()
        glut_init_display_mode(
            GLUTDisplayMode.RGBA | GLUTDisplayMode.DOUBLE | GLUTDisplayMode.DEPTH
        )
        glut_init_window_size(self.width, self.height)
        glut_create_window(self.title)

        glut_display_func(self.render)
        glut_reshape_func(self.reshape)
        glut_keyboard_func(self.keyboard)
        glut_mouse_func(self.mouse)
        glut_motion_func(self.motion)
        glut_idle_func(self.idle)

    def init_gl(self) -> None:
        """Initialize common fixed-function OpenGL state."""
        gl_initialize_background(RGBAColor(0.1, 0.1, 0.2, 1.0))
        gl_enable_capability_list(
            [
                GLFixedFunctionCapability.LIGHTING,
                GLFixedFunctionCapability.LIGHT0,
                GLCapability.COLOR_MATERIAL,
            ]
        )
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )
        gl_legacy_lighting()

    def render(self) -> None:
        """Render one frame."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        self.camera.apply()
        self.draw_scene()
        glut_swap_buffers()

    @abstractmethod
    def draw_scene(self) -> None:
        """Draw renderer-specific geometry."""

    def idle(self) -> None:
        """Idle callback; override for animation."""

    def keyboard(self, key, x, y) -> None:
        """Handle keyboard input; shared keys plus subclass hooks."""
        del x, y
        if key == b"\x1b":
            sys.exit(0)
        elif key == b"r":
            self.camera.rotation.reset()
        else:
            self.handle_key(key)
        glut_post_redisplay()

    def handle_key(self, key: bytes) -> None:
        """Handle renderer-specific keyboard input."""

    def reshape(self, width: int, height: int) -> None:
        """Handle GLUT window resize."""
        self.width = width
        self.height = height
        self.viewport.width = width
        self.viewport.height = height
        self.viewport.apply()
        self.projection.apply(self.projection_config.with_size(width, height))

    def mouse(self, button, state, x, y) -> None:
        """Handle common camera mouse interaction."""
        if button == GLUTMouseButton.LEFT:
            if state == GLUTMouseState.DOWN:
                self.camera.rotation.press(x, y)
            else:
                self.camera.rotation.release()
        elif button == GLUTMouseButton.WHEEL_UP:
            self.camera.distance = max(1.0, self.camera.distance - 0.5)
        elif button == GLUTMouseButton.WHEEL_DOWN:
            self.camera.distance = min(20.0, self.camera.distance + 0.5)
        glut_post_redisplay()

    def motion(self, x, y) -> None:
        """Handle camera rotation."""
        if self.camera.rotation.drag(x, y) is None:
            return
        self.camera.rotation.clamp_x()
        glut_post_redisplay()

    def startup_message(self) -> None:
        """Print application startup information."""

    def run(self) -> None:
        """Run the GLUT application."""
        self.init_glut()
        self.init_gl()
        self.startup_message()
        glut_main_loop()
