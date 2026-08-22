#!/usr/bin/env python3
"""Minimal Legacy PicoGL Cube - Maximum Compatibility.

This is the most basic cube renderer that works on any system with basic
OpenGL support, including older macOS systems.

Features:
- Built-in immediate-mode cube (no modern VAO/VBO)
- PicoGL wrappers for GLUT, camera, viewport, and GL state
- Interactive rotation and zoom
- Colored cube data from PicoGL cube_data
"""

from __future__ import annotations

import os
import sys

import numpy as np

from picogl.backend.gl.api.color import gl_color_3f, gl_color_rgb
from picogl.backend.gl.api.vertex.vertex_3f import gl_vertex_3f
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.gl.state.scoped import disabled
from picogl.backend.glut import glut_post_redisplay
from picogl.backend.glut.cube_data import CUBE_COLORS, CUBE_VERTICES
from picogl.backend.legacy.core.renderer import LegacyRenderer
from picogl.core.rgbcolor import RGBColor
from picogl.polygon.mode import polygon_mode

# Check for display before initializing GLUT
if os.environ.get("DISPLAY") is None and os.name != "nt":
    print("❌ No display available. This requires a graphical environment.")
    print("   Try running on a system with X11, Wayland, or macOS display.")
    sys.exit(1)


class MinimalCubeRenderer(LegacyRenderer):
    """Minimal cube renderer using immediate-mode OpenGL."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Minimal Legacy Cube",
    ) -> None:
        super().__init__(width=width, height=height, title=title)
        self.wireframe_mode = False
        self.show_normals = False
        self.auto_rotate = False

        self.vertices = CUBE_VERTICES.reshape(-1, 3)
        self.colors = CUBE_COLORS.reshape(-1, 3)

    def draw_scene(self) -> None:
        self.draw_cube()

    def draw_cube(self) -> None:
        """Draw the cube using immediate mode via PicoGL wrappers."""
        if self.wireframe_mode:
            with disabled(GLFixedFunctionCapability.LIGHTING):
                with polygon_mode(GLFillMode.LINE):
                    gl_color_rgb(RGBColor.RED)
                    self._emit_triangles(colored=False)
            return

        self._emit_triangles(colored=True)
        if self.show_normals:
            self.draw_normals()

    def _emit_triangles(self, *, colored: bool) -> None:
        with gl_immediate_drawing(GLDrawMode.TRIANGLES):
            for vertex_idx in range(len(self.vertices)):
                if colored:
                    color = self.colors[vertex_idx]
                    gl_color_rgb(RGBColor(color[0], color[1], color[2]))
                vertex = self.vertices[vertex_idx]
                gl_vertex_3f(float(vertex[0]), float(vertex[1]), float(vertex[2]))

    def draw_normals(self) -> None:
        """Draw simplified triangle normal vectors."""
        with disabled(GLFixedFunctionCapability.LIGHTING):
            gl_color_rgb(RGBColor.GREEN)
            with gl_immediate_drawing(GLDrawMode.LINES):
                for i in range(0, len(self.vertices), 6):
                    if i + 2 >= len(self.vertices):
                        continue
                    v1 = self.vertices[i]
                    v2 = self.vertices[i + 1]
                    v3 = self.vertices[i + 2]

                    edge1 = v2 - v1
                    edge2 = v3 - v1
                    normal = np.cross(edge1, edge2)
                    norm = np.linalg.norm(normal)
                    if norm == 0.0:
                        continue
                    normal = normal / norm
                    center = (v1 + v2 + v3) / 3.0

                    gl_vertex_3f(float(center[0]), float(center[1]), float(center[2]))
                    gl_vertex_3f(
                        float(center[0] + normal[0] * 0.5),
                        float(center[1] + normal[1] * 0.5),
                        float(center[2] + normal[2] * 0.5),
                    )

    def handle_key(self, key: bytes) -> None:
        if key == b"w":
            self.wireframe_mode = not self.wireframe_mode
        elif key == b"f":
            self.wireframe_mode = False
        elif key == b"n":
            self.show_normals = not self.show_normals
        elif key == b"+":
            self.camera.distance = max(1.0, self.camera.distance - 0.5)
        elif key == b"-":
            self.camera.distance = min(20.0, self.camera.distance + 0.5)
        elif key == b" ":
            self.auto_rotate = not self.auto_rotate

    def idle(self) -> None:
        if self.auto_rotate:
            self.camera.rotation.y += 0.5
            glut_post_redisplay()

    def startup_message(self) -> None:
        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Toggle wireframe mode")
        print("   F: Fill mode")
        print("   N: Toggle normals display")
        print("   +/-: Zoom in/out")
        print("   Space: Toggle auto-rotation")
        print("   ESC: Exit")
        print("\n🚀 Starting minimal legacy cube renderer...")
        print(
            f"   Rendering {len(self.vertices)} vertices with {len(self.colors)} colors"
        )


def main() -> None:
    """Main function."""
    print("🧪 Minimal Legacy PicoGL Cube")
    print("=" * 40)

    try:
        renderer = MinimalCubeRenderer(
            width=800,
            height=600,
            title="Minimal Legacy PicoGL Cube (OpenGL 1.x Compatible)",
        )
        renderer.run()
    except Exception as exc:
        print(f"❌ Error running minimal cube renderer: {exc}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
