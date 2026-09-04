"""
Tutorial 01 — Colored Cube (PicoGL).

Uses MeshData + RenderWindow / ObjectRenderer instead of raw VBOs and
utils.shader_loader.Shader. Mouse drag rotates; wheel zooms; R resets via
GlutRendererWindow.
"""

import os
import sys
from pathlib import Path

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
# Must be set before any OpenGL / picogl import.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.data.cube_data import (g_color_buffer_data,
                                            g_vertex_buffer_data)
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow

_EXAMPLES_DIR = Path(__file__).resolve().parent
_GLSL_DIR = _EXAMPLES_DIR / "glsl" / "tu01"


def main() -> None:
    data = MeshData.from_raw(
        vertices=g_vertex_buffer_data,
        colors=g_color_buffer_data,
    )
    win = RenderWindow(
        width=800,
        height=600,
        title="Tutorial 01 - Colored Cube",
        data=data,
        glsl_dir=_GLSL_DIR,
        base_dir=_EXAMPLES_DIR,
    )
    # Closer eye than the default RenderWindow distance so the cube fills the view.
    win.zoom_distance = 3.0
    win.distance_threshold = 1.5
    win.sync_zoom_to_context()
    win.initialize()
    win.run()


if __name__ == "__main__":
    main()
