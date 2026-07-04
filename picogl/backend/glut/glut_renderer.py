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
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace

# from picogl.examples.legacy_cube_fixed import LegacyCubeRenderer
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity, gl_viewport
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import (
    GLCapability,
    GLColorMaterialMode,
    GLFace,
    GLFillMode,
)
from picogl.backend.gl.wrappers.clear import gl_clear, gl_clear_color
from picogl.backend.gl.wrappers.color import gl_color_3f
from picogl.backend.gl.wrappers.glu import glu_look_at
from picogl.backend.gl.wrappers.matrix import gl_matrix_mode
from picogl.backend.gl.wrappers.polygon_mode import gl_polygon_mode
from picogl.backend.gl.wrappers.rotate import gl_rotate_f
from picogl.backend.glut.cube_data import CUBE_COLORS, CUBE_VERTICES

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
        self.width = width
        self.height = height
        self.title = title
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
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

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glutIdleFunc(self.idle)

    def initialize_glut(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title.encode("utf-8"))

        # Set callbacks
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)

    def init_gl(self):
        """Initialize OpenGL state."""
        gl_clear_color(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        GLCapabilityDriver.enable(GL_DEPTH_TEST)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)
        GLCapabilityDriver.enable(GLCapability.COLOR_MATERIAL)
        gl_color_material(
            GLFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )

        gl_legacy_lighting()

    def load_cube_data(self):
        """Load cube data using PicoGL LegacyGLMesh."""
        try:
            # Create mesh data
            mesh_data = MeshData.from_raw(
                vertices=self.vertices.flatten(), colors=self.colors.flatten()
            )

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
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        gl_load_identity()

        # Set up camera
        glu_look_at(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        gl_rotate_f(self.rotation_x, 1, 0, 0)
        gl_rotate_f(self.rotation_y, 0, 1, 0)

        # Draw the cube
        if self.mesh:
            try:
                if self.wireframe_mode:
                    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
                    gl_disable(GLFixedFunctionCapability.LIGHTING)
                else:
                    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
                    GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)

                self.mesh.draw()

                # Reset polygon mode
                gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
                GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)

            except Exception as e:
                print(f"Error drawing mesh: {e}")
                # Fallback: draw a simple wireframe cube
                self.draw_fallback_cube()
        else:
            # Fallback: draw a simple wireframe cube
            self.draw_fallback_cube()

        glutSwapBuffers()

    def draw_fallback_cube(self):
        """Draw a simple wireframe cube as fallback."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        red_rgb = (1.0, 0.0, 0.0)
        gl_color_3f(red_rgb)  # Red wireframe
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        glutWireCube(2.0)
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    def keyboard(self, key, x, y):
        """Keyboard callback."""
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.rotation_x = 0.0
            self.rotation_y = 0.0
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

        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        """Mouse callback."""
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.last_mouse_x = x
                self.last_mouse_y = y
            else:
                self.last_mouse_x = None
                self.last_mouse_y = None
        elif button == 3:  # Mouse wheel up
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif button == 4:  # Mouse wheel down
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        glutPostRedisplay()

    def motion(self, x, y):
        """Mouse motion callback."""
        if self.last_mouse_x is not None and self.last_mouse_y is not None:
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            # Clamp rotation
            self.rotation_x = max(-90, min(90, self.rotation_x))

            self.last_mouse_x = x
            self.last_mouse_y = y
            glutPostRedisplay()

    def idle(self):
        """Idle callback for animation."""
        if self.auto_rotate:
            self.rotation_y += 0.5
            glutPostRedisplay()

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

        glutMainLoop()


def main():
    """Main function."""
    print("🧪 Legacy PicoGL Cube")
    print("=" * 40)

    try:
        from picogl.examples.legacy_cube_fixed import LegacyCubeRenderer

        renderer = LegacyCubeRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Cube (OpenGL 1.x/2.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running legacy cube renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
