#!/usr/bin/env python3
"""Minimal Legacy PicoGL Teapot - Maximum Compatibility.

This is the most basic teapot renderer possible that works on any system
with basic OpenGL support, including older macOS systems.

Features:
- Uses only built-in OpenGL primitives
- No external dependencies beyond PyOpenGL
- No PicoGL library required
- Works with OpenGL 1.x/2.x
- Interactive rotation and zoom
- Minimal error handling for maximum compatibility
"""

import os
import sys

from picogl.core.vec3 import Vec3
from picogl.examples.cube_with_controls import GLViewTransform
from picogl.core.rgbcolor import RGBAColor
from picogl.core.setup.camera import gl_setup_camera
from picogl.core.setup.view import gl_setup_view

from picogl.backend.gl.api.clear import gl_clear_rgba_color
from picogl.backend.gl.api.color import gl_color_3f, gl_color_material
from picogl.backend.gl.api.enable import gl_enable, toggle_capability
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace, GLPipelineCapability)
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity, gl_viewport
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import (GLCapability, GLColorMaterialMode,
                                          GLFillMode)
from picogl.backend.glu.perspective import glu_perspective
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.glut_renderer import GlutRenderer
from picogl.backend.glut.teapot import glut_solid_teapot

# Check for display before importing OpenGL
if os.environ.get("DISPLAY") is None and os.name != "nt":
    print("❌ No display available. This requires a graphical environment.")
    print("   Try running on a system with X11, Wayland, or macOS display.")
    sys.exit(1)

try:
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except ImportError as e:
    print(f"❌ Failed to import OpenGL modules: {e}")
    print("   Install with: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)


def gl_init_capabilities():
    """init capabilities"""
    capabilities_to_enable = [
        GLPipelineCapability.DEPTH_TEST,
        GLFixedFunctionCapability.LIGHTING,
        GLFixedFunctionCapability.LIGHT0,
        GLCapability.COLOR_MATERIAL
    ]
    for capability in capabilities_to_enable:
        gl_enable(capability)


class MinimalTeapotRenderer(GlutRenderer):
    """Minimal teapot renderer using only built-in OpenGL primitives."""

    def __init__(self, width=800, height=600, title="Minimal Legacy Teapot"):
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
        # self.view = GLViewTransform(zoom=self.zoom_distance, rotation=Vec3(0.0, 0.0, 0.0))
        self.view = GLViewTransform(zoom=-50, rotation=Vec3(0.0, 0.0, 0.0))

    def init_gl(self):
        """Initialize OpenGL state."""
        gl_clear_rgba_color(RGBAColor(0.1, 0.1, 0.2, 1.0))  # Dark blue background
        gl_init_capabilities()
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )
        gl_legacy_lighting()

    def display(self):
        """Display callback - render the scene."""
        gl_setup_view()

        # Set up camera
        gl_setup_camera(self.zoom_distance)

        # Apply rotations
        gl_rotate_f(angle=self.rotation_x, x=1, y=0, z=0)
        gl_rotate_f(angle=self.rotation_y, x=0, y=1, z=0)

        # Draw the teapot
        self.draw_teapot()

        glut_swap_buffers()

    def draw_teapot(self):
        """Draw the teapot using built-in OpenGL primitives."""
        # Set polygon mode
        red_wireframe = (1.0, 0.0, 0.0)
        red_teapot = (0.8, 0.2, 0.2)  # Red teapot
        if self.wireframe_mode:
            fill_mode = GLFillMode.LINE
            color = red_wireframe
        else:
            fill_mode = GLFillMode.FILL
            color = red_teapot
        gl_color_3f(color)
        toggle_capability(
            enabled=not self.wireframe_mode,
            capability=GLFixedFunctionCapability.LIGHTING,
        )
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, fill_mode)
        # Draw the teapot
        glut_solid_teapot(1.0)

        # Reset polygon mode
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        glu_perspective(45.0, float(width) / float(height), 0.1, 100.0)
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    def run(self):
        """Run the application."""
        self.initialize_glut()
        self.init_gl()

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Toggle wireframe mode")
        print("   F: Fill mode")
        print("   +/-: Zoom in/out")
        print("   ESC: Exit")
        print("\n🚀 Starting minimal legacy teapot renderer...")

        glutMainLoop()


def main():
    """Main function."""
    print("🧪 Minimal Legacy PicoGL Teapot")
    print("=" * 40)

    try:
        renderer = MinimalTeapotRenderer(
            width=800,
            height=600,
            title="Minimal Legacy PicoGL Teapot (OpenGL 1.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running minimal teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
