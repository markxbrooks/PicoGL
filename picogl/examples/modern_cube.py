"""Minimal PicoGL Cube. Compare to modern_colored_cube.py"""

import os
import sys
from pathlib import Path

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
# Must be set before any OpenGL / picogl import.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.data.cube_data import g_color_buffer_data, g_vertex_buffer_data
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow

BASE_DIR = Path(__file__).resolve().parent
GLSL_DIR = Path(__file__).parent / "glsl" / "tu01"


def main() -> None:
    """Set up the colored object dat and show it"""
    data = MeshData.from_raw(vertices=g_vertex_buffer_data, colors=g_color_buffer_data)
    render_window = RenderWindow(
        width=800,
        height=600,
        title="Cube window",
        data=data,
        glsl_dir=GLSL_DIR,
        base_dir=BASE_DIR,
    )
    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    main()
