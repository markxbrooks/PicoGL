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

from backend.gl.api.enable import gl_disable
from backend.gl.api.legacy.matrix import gl_matrix_mode_context
from core.rgbcolor import RGBColor, RGBAColor
from core.setup.camera import gl_setup_camera
from core.setup.view import gl_setup_view
from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.backend.gl.api.color import gl_color_rgb, gl_color_material
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace, GLPipelineCapability
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.enums.legacy.scale import (gl_rotatef,
                                                  gl_viewport)
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import (GLCapability, GLColorMaterialMode, GLFillMode)
from picogl.backend.glu.perspective import glu_perspective
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.cube import glut_wire_cube
from picogl.backend.glut.display import glut_post_redisplay
from picogl.backend.glut.glut_renderer import GlutRenderer

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


class LegacyCubeRenderer(GlutRenderer):
    """Legacy cube renderer using PicoGL LegacyGLMesh."""

    def __init__(
        self,
        width: object = 800,
        height: object = 600,
        title: object = "Legacy PicoGL Cube",
    ) -> None:
        super().__init__(width, height, title)
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
        self.vertices = np.array(
            [
                -1.0,
                -1.0,
                -1.0,  # 0
                -1.0,
                -1.0,
                1.0,  # 1
                -1.0,
                1.0,
                1.0,  # 2
                1.0,
                1.0,
                -1.0,  # 3
                -1.0,
                -1.0,
                -1.0,  # 4
                -1.0,
                1.0,
                -1.0,  # 5
                1.0,
                -1.0,
                1.0,  # 6
                -1.0,
                -1.0,
                -1.0,  # 7
                1.0,
                -1.0,
                -1.0,  # 8
                1.0,
                1.0,
                -1.0,  # 9
                1.0,
                -1.0,
                -1.0,  # 10
                -1.0,
                -1.0,
                -1.0,  # 11
                -1.0,
                -1.0,
                -1.0,  # 12
                -1.0,
                1.0,
                1.0,  # 13
                -1.0,
                1.0,
                -1.0,  # 14
                1.0,
                -1.0,
                1.0,  # 15
                -1.0,
                -1.0,
                1.0,  # 16
                -1.0,
                -1.0,
                -1.0,  # 17
                -1.0,
                1.0,
                1.0,  # 18
                -1.0,
                -1.0,
                1.0,  # 19
                1.0,
                -1.0,
                1.0,  # 20
                1.0,
                1.0,
                1.0,  # 21
                1.0,
                -1.0,
                -1.0,  # 22
                1.0,
                1.0,
                -1.0,  # 23
                1.0,
                -1.0,
                -1.0,  # 24
                1.0,
                1.0,
                1.0,  # 25
                1.0,
                -1.0,
                1.0,  # 26
                1.0,
                1.0,
                1.0,  # 27
                1.0,
                1.0,
                -1.0,  # 28
                -1.0,
                1.0,
                -1.0,  # 29
                1.0,
                1.0,
                1.0,  # 30
                -1.0,
                1.0,
                -1.0,  # 31
                -1.0,
                1.0,
                1.0,  # 32
                1.0,
                1.0,
                1.0,  # 33
                -1.0,
                1.0,
                1.0,  # 34
                1.0,
                -1.0,
                1.0,  # 35
            ],
            dtype=np.float32,
        )

        self.colors = np.array(
            [
                0.583,
                0.771,
                0.014,  # 0
                0.609,
                0.115,
                0.436,  # 1
                0.327,
                0.483,
                0.844,  # 2
                0.822,
                0.569,
                0.201,  # 3
                0.435,
                0.602,
                0.223,  # 4
                0.310,
                0.747,
                0.185,  # 5
                0.597,
                0.770,
                0.761,  # 6
                0.559,
                0.436,
                0.730,  # 7
                0.359,
                0.583,
                0.152,  # 8
                0.483,
                0.596,
                0.789,  # 9
                0.559,
                0.861,
                0.639,  # 10
                0.195,
                0.548,
                0.859,  # 11
                0.014,
                0.184,
                0.576,  # 12
                0.771,
                0.328,
                0.970,  # 13
                0.406,
                0.615,
                0.116,  # 14
                0.676,
                0.977,
                0.133,  # 15
                0.971,
                0.572,
                0.833,  # 16
                0.140,
                0.616,
                0.489,  # 17
                0.997,
                0.513,
                0.064,  # 18
                0.945,
                0.719,
                0.592,  # 19
                0.543,
                0.021,
                0.978,  # 20
                0.279,
                0.317,
                0.505,  # 21
                0.167,
                0.620,
                0.077,  # 22
                0.347,
                0.857,
                0.137,  # 23
                0.055,
                0.953,
                0.042,  # 24
                0.714,
                0.505,
                0.345,  # 25
                0.783,
                0.290,
                0.734,  # 26
                0.722,
                0.645,
                0.174,  # 27
                0.302,
                0.455,
                0.848,  # 28
                0.225,
                0.587,
                0.040,  # 29
                0.517,
                0.713,
                0.338,  # 30
                0.053,
                0.959,
                0.120,  # 31
                0.393,
                0.621,
                0.362,  # 32
                0.673,
                0.211,
                0.457,  # 33
                0.820,
                0.883,
                0.371,  # 34
                0.982,
                0.099,
                0.879,  # 35
            ],
            dtype=np.float32,
        )

        # Reshape for easier access
        self.vertices = self.vertices.reshape(-1, 3)
        self.colors = self.colors.reshape(-1, 3)

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glutIdleFunc(self.idle)

    def init_gl(self):
        """Initialize OpenGL state."""
        gl_clear_rgba_color(RGBAColor(0.1, 0.1, 0.2, 1.0))  # Dark blue background
        GLCapabilityDriver.enable(GLPipelineCapability.DEPTH_TEST)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHT0)
        GLCapabilityDriver.enable(GLCapability.COLOR_MATERIAL)
        gl_color_material(GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE)

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
        gl_setup_view()

        gl_setup_camera(self.zoom_distance)

        # Apply rotations
        gl_rotatef(self.rotation_x, 1, 0, 0)
        gl_rotatef(self.rotation_y, 0, 1, 0)

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

        glut_swap_buffers()

    def draw_fallback_cube(self):
        """Draw a simple wireframe cube as fallback."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        gl_color_rgb(RGBColor.RED)  # Red wireframe
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        glut_wire_cube(2.0)
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        with gl_matrix_mode_context():
            glu_perspective(45.0, float(width) / float(height), 0.1, 100.0)

    def idle(self):
        """Idle callback for animation."""
        if self.auto_rotate:
            self.rotation_y += 0.5
            glut_post_redisplay()


def main():
    """Main function."""
    print("🧪 Legacy PicoGL Cube")
    print("=" * 40)

    try:
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
