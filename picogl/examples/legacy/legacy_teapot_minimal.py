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

from picogl.core.draw.teapot import draw_teapot
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.glut_renderer import GlutRenderer

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


class MinimalTeapotRenderer(GlutRenderer):
    """Minimal teapot renderer using only built-in OpenGL primitives."""

    def __init__(self, width=800, height=600, title="Minimal Legacy Teapot"):
        super().__init__(width, height, title)
        self.update_size(height, width)
        self.title = title
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.zoom_distance = 5.0
        self.wireframe_mode = False

    def draw_mesh(self):
        # Draw the teapot
        draw_teapot(self.wireframe_mode)

        glut_swap_buffers()

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
