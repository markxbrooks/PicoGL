"""Minimal PicoGL Cube. Compare to modern_colored_cube.py"""

from pathlib import Path

from picogl.examples.data.cube_data import g_color_buffer_data, g_vertex_buffer_data
from picogl.globals import PICOGL_EXAMPLES_DIR
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow

BASE_DIR = Path(__file__).resolve().parent
GLSL_DIR = PICOGL_EXAMPLES_DIR / "glsl" / "tu01"


def main() -> None:
    """Set up the colored cube mesh and show it."""
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
