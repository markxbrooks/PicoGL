"""Simple Legacy PicoGL Teapot - No external files required.

This is the simplest possible teapot renderer that works on any system
with basic OpenGL support, including older macOS systems.

Features:
- Uses only built-in OpenGL primitives (glutSolidTeapot)
- No external OBJ files required
- No modern shaders required
- Works with OpenGL 1.x/2.x
- Interactive rotation and zoom
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

from backend.gl.api.color import gl_color_rgb
from backend.gl.api.legacy.matrix import gl_matrix_mode_context
from core.setup.camera import gl_setup_camera
from core.setup.view import gl_setup_view
from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.backend.gl.api.color import gl_color_3f, gl_color_material
from picogl.backend.gl.api.enable import gl_disable, gl_enable
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.api.vertex.vertex_3f import gl_vertex_3f
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace, GLPipelineCapability)
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity, gl_viewport
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import (GLCapability, GLColorMaterialMode,
                                          GLFillMode)
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.glu.perspective import glu_perspective
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.display import glut_post_redisplay
from picogl.backend.glut.glut_renderer import GlutRenderer
from picogl.backend.glut.teapot import glut_solid_teapot
from picogl.core.rgbcolor import RGBColor, RGBAColor


class SimpleTeapotRenderer(GlutRenderer):
    """Simple teapot renderer using only built-in OpenGL primitives."""

    def __init__(self, width=800, height=600, title="Simple Legacy Teapot"):
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
        self.show_normals = False

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glutIdleFunc(self.idle)

    def init_gl(self):
        """Initialize OpenGL state."""
        try:
            dark_blue_background = RGBAColor(0.1, 0.1, 0.2, 1.0)
            gl_clear_rgba_color(dark_blue_background)  # Dark blue background
            gl_enable(GLPipelineCapability.DEPTH_TEST)
            gl_enable(GLFixedFunctionCapability.LIGHTING)
            gl_enable(GLFixedFunctionCapability.LIGHT0)
            gl_enable(GLCapability.COLOR_MATERIAL)
            gl_color_material(
                GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
            )

            gl_legacy_lighting()

        except Exception as e:
            print(f"Warning: OpenGL initialization issue: {e}")
            print("Continuing with basic rendering...")

    def display(self):
        """Display callback - render the scene."""
        gl_setup_view()

        # Set up camera
        gl_setup_camera(self.zoom_distance)

        # Apply rotations
        gl_rotate_f(self.rotation_x, 1, 0, 0)
        gl_rotate_f(self.rotation_y, 0, 1, 0)

        # Draw the teapot
        self.draw_teapot()

        glut_swap_buffers()

    def draw_teapot(self):
        """Draw the teapot using built-in OpenGL primitives."""
        # Set polygon mode
        if self.wireframe_mode:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
            gl_disable(GLFixedFunctionCapability.LIGHTING)
            red_teapot = RGBColor(1.0, 0.0, 0.0)
            gl_color_3f(*red_teapot.tuple)  # Red wireframe
        else:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
            gl_enable(GLFixedFunctionCapability.LIGHTING)
            gl_color_rgb(RGBColor(0.8, 0.2, 0.2))  # Red teapot

        # Draw the teapot
        glut_solid_teapot(1.0)

        # Draw normals if enabled
        if self.show_normals and not self.wireframe_mode:
            self.draw_normals()

        # Reset polygon mode
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def draw_normals(self):
        """Draw normal vectors (simplified)."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        gl_color_3f((0.0, 1.0, 0.0))  # Green normals
        with gl_immediate_drawing(GLDrawMode.LINES):
            # Draw a few normal vectors for demonstration
            for i in range(0, 360, 30):
                angle = i * 3.14159 / 180.0
                x = 0.5 * np.cos(angle)
                y = 0.5 * np.sin(angle)
                z = 0.0

                # Normal vector (simplified)
                nx = x
                ny = y
                nz = z

                gl_vertex_3f(x, y, z)
                glVertex3f(x + nx * 0.2, y + ny * 0.2, z + nz * 0.2)

        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        with gl_matrix_mode_context():
            glu_perspective(45.0, float(width) / float(height), 0.1, 100.0)

    def idle(self):
        """Idle callback for animation."""
        if getattr(self, "auto_rotate", False):
            self.rotation_y += 0.5
            glut_post_redisplay()


def main():
    """Main function."""
    try:
        # Check if we're in a headless environment
        import os

        if os.environ.get("DISPLAY") is None and os.name != "nt":
            print("❌ No display available. This requires a graphical environment.")
            print("   Try running on a system with X11, Wayland, or macOS display.")
            return

        renderer = SimpleTeapotRenderer(
            width=800,
            height=600,
            title="Simple Legacy PicoGL Teapot (OpenGL 1.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running simple teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
