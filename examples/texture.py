"""
Demonstrating textures - compare to tu02_texture_without_normal.py
"""

from pathlib import Path

from examples import g_uv_buffer_data, g_vertex_buffer_data
from picogl.renderer import MeshDataLegacy
from picogl.ui.backend.glut.window.texture import TextureWindow

BASE_DIR = Path(__file__).resolve().parent
GLSL_DIR = BASE_DIR / "glsl" / "tu02"


def main() -> None:
    """Set up the cube and draw it with texture."""
    mesh_data = MeshDataLegacy.from_raw(vertices=g_vertex_buffer_data, uvs=g_uv_buffer_data)
    render_window = TextureWindow(
        width=800,
        height=600,
        title="texture window",
        data=mesh_data,
        base_dir=BASE_DIR,
        glsl_dir=GLSL_DIR,
        use_texture=True,
    )
    render_window.initializeGL()
    render_window.run()


if __name__ == "__main__":
    main()
