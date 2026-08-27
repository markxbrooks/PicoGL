#!/usr/bin/env python3
"""Legacy PicoGL Cube - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

import os
import sys

import numpy as np

# Before any OpenGL import: GLX under Wayland, Apple GLUT on macOS.
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from core.view.transform import GLViewTransform
from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.cube_data import CUBE_COLORS, CUBE_VERTICES
from picogl.backend.glut.display import (
    glut_display_func,
    glut_idle_func,
    glut_keyboard_func,
    glut_motion_func,
    glut_mouse_func,
    glut_post_redisplay,
    glut_reshape_func,
)
from picogl.backend.glut.enums import GLUTDisplayMode, GLUTMouseButton, GLUTMouseState
from picogl.backend.glut.idle import glut_idle_func
from picogl.backend.glut.init import (
    glut_create_window,
    glut_init,
    glut_init_display_mode,
    glut_init_window_size,
    glut_main_loop,
)
from picogl.backend.legacy.core.camera.projection_state import GLUProjectionState
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.state import GLViewport
from picogl.core.camera import ProjectionConfig
from picogl.core.draw.cube import draw_fallback_cube
from picogl.core.draw.mesh.legacy import draw_legacy_mesh
from picogl.core.rgbcolor import RGBAColor
from picogl.core.setup.camera import gl_setup_camera
from picogl.core.setup.view import gl_setup_view
from picogl.core.vec3 import Vec3
from picogl.ui.backend.glut.mouse import RotationInteraction

# Check for display before importing OpenGL
if os.environ.get("DISPLAY") is None and os.name != "nt":
    print("❌ No display available. This requires a graphical environment.")
    print("   Try running on a system with X11, Wayland, or macOS display.")
    sys.exit(1)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except ImportError as e:
    print(f"❌ Failed to import OpenGL modules: {e}")
    print("   Install with: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

try:
    from picogl.renderer import MeshData
    from picogl.renderer.legacy_glmesh import LegacyGLMesh
except ImportError as e:
    print(f"❌ Failed to import PicoGL modules: {e}")
    print("   Install with: pip install picogl")
    print("   Or use legacy_cube_minimal.py instead")
    sys.exit(1)


class GlutRenderer:
    """Legacy cube renderer using PicoGL LegacyGLMesh."""

    def __init__(self, width=800, height=600, title="Legacy Glut Renderer"):
        self.viewport = GLViewport(width=width, height=height)
        self.projection_config = ProjectionConfig()
        self.projection = GLUProjectionState()
        self.width = width
        self.height = height
        self.title = title
        self.rotation = RotationInteraction()
        self.zoom_distance = 5.0
        self.wireframe_mode = False
        self.auto_rotate = False
        self.mesh = None

        # Cube data (from cube_data.py)
        self.vertices = CUBE_VERTICES

        self.colors = CUBE_COLORS

        # Reshape for easier access
        self.vertices = self.vertices.reshape(-1, 3)
        self.colors = self.colors.reshape(-1, 3)
        self.view = GLViewTransform(zoom=-50, rotation=Vec3(0.0, 0.0, 0.0))

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glut_idle_func(self.idle)

    def initialize_glut(self):
        glut_init(sys.argv)
        glut_init_display_mode(
            GLUTDisplayMode.RGBA | GLUTDisplayMode.DOUBLE | GLUTDisplayMode.DEPTH
        )
        glut_init_window_size(self.width, self.height)
        glut_create_window(self.title)

        # Set callbacks
        glut_display_func(self.display)
        glut_reshape_func(self.reshape)
        glut_keyboard_func(self.keyboard)
        glut_mouse_func(self.mouse)
        glut_motion_func(self.motion)

    def init_gl(self):
        """Initialize OpenGL state."""
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

    def load_cube_data(self):
        """Load cube data using PicoGL LegacyGLMesh."""
        try:
            # Create faces array (triangles)
            faces = np.arange(len(self.vertices)).reshape(-1, 3)

            # Create legacy mesh
            self.mesh = LegacyGLMesh(
                vertices=self.vertices,
                faces=faces,
                colors=self.colors,
            )

            # Upload mesh to GPU
            self.mesh.upload()
            print(
                f"✅ Loaded cube with {len(self.vertices)} vertices using LegacyGLMesh"
            )
            return True

        except Exception as e:
            print(f"❌ Error loading cube data: {e}")
            return False

    def display(self):
        """Display callback - render the scene."""
        gl_setup_view()

        # Set up camera
        gl_setup_camera(self.zoom_distance)

        self.apply_rotations()

        self.view.apply()

        self.draw_mesh()

    def apply_rotations(self):
        """Apply rotations"""
        gl_rotate_f(self.rotation.x, 1, 0, 0)
        gl_rotate_f(self.rotation.y, 0, 1, 0)

    def draw_mesh(self):
        """Draw the cube"""
        if self.mesh:
            try:
                draw_legacy_mesh(self.mesh, self.wireframe_mode)

            except Exception as e:
                print(f"Error drawing mesh: {e}")
                # Fallback: draw a simple wireframe cube
                draw_fallback_cube()
        else:
            # Fallback: draw a simple wireframe cube
            draw_fallback_cube()

        glut_swap_buffers()

    def update_size(self, height, width):
        self.viewport.width = width
        self.viewport.height = height
        self.width = width
        self.height = height

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.update_size(height, width)
        self.update_viewport()
        self.update_perspective(height, width)

    def update_perspective(self, height, width):
        self.projection.apply(self.projection_config.with_size(width, height))

    def update_viewport(self, height=None, width=None):
        if width is not None:
            self.viewport.width = width
        if height is not None:
            self.viewport.height = height
        self.viewport.apply()

    def keyboard(self, key, x, y):
        """Keyboard callback."""
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.rotation.reset()
        elif key == b"w":  # Toggle wireframe mode
            self.wireframe_mode = not self.wireframe_mode
        elif key == b"f":  # Fill mode
            self.wireframe_mode = False
        elif key == b"+":  # Zoom in
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif key == b"-":  # Zoom out
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        elif key == b" ":  # Space bar - auto rotate
            self.auto_rotate = not self.auto_rotate

        glut_post_redisplay()

    def mouse(self, button, state, x, y):
        """Mouse callback."""
        if button == GLUTMouseButton.LEFT:
            if state == GLUTMouseState.DOWN:
                self.rotation.press(x, y)
            else:
                self.rotation.release()
        elif button == GLUTMouseButton.WHEEL_UP:  # Mouse wheel up
            self.view.zoom = max(1.0, self.zoom_distance - 0.5)
            # self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif button == GLUTMouseButton.WHEEL_DOWN:  # Mouse wheel down
            self.view.zoom = min(20.0, self.zoom_distance + 0.5)
            # self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        glut_post_redisplay()

    def motion(self, x, y):
        """Mouse motion callback."""
        if self.rotation.drag(x, y) is None:
            return
        self.rotation.clamp_x()
        glut_post_redisplay()

    def idle(self):
        """Idle callback for animation."""
        if self.auto_rotate:
            self.rotation.y += 0.5
            glut_post_redisplay()

    def run(self):
        """Run the application."""
        self.init_glut()
        self.init_gl()

        # Load cube data
        if not self.load_cube_data():
            print("   Using fallback wireframe cube instead.")

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Toggle wireframe mode")
        print("   F: Fill mode")
        print("   +/-: Zoom in/out")
        print("   Space: Toggle auto-rotation")
        print("   ESC: Exit")
        print("\n🚀 Starting legacy renderer...")

        glut_main_loop()


def main():
    """Main function."""
    print("🧪 Legacy PicoGL Cube")
    print("=" * 40)

    try:
        renderer = GlutRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Cube (OpenGL 1.x/2.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running legacy cube renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   On Linux/Wayland, try: PYOPENGL_PLATFORM=glx python ...")
        print("   On macOS, try running from Terminal.app or iTerm2.")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
