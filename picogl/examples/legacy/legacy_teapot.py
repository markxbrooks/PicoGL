"""Minimal Legacy PicoGL Teapot."""

from pathlib import Path

from picogl.globals import PICOGL_EXAMPLES_DIR
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow
from picogl.utils.loader.object import ObjectLoader

BASE_DIR = Path(__file__).resolve().parent.parent
GLSL_DIR = PICOGL_EXAMPLES_DIR / "glsl" / "teapot"


def main() -> None:
    """Set up the teapot object and show it."""
    object_file_name = PICOGL_EXAMPLES_DIR / "data" / "teapot.obj"
    obj_loader = ObjectLoader(object_file_name)
    teapot_data = obj_loader.to_array_style()
    data = MeshData.from_raw(
        vertices=teapot_data.vertices,
        normals=teapot_data.normals,
        colors=([[1.0, 0.0, 0.0]] * (len(teapot_data.vertices) // 3)),
    )
    render_window = RenderWindow(
        width=800,
        height=600,
        title="Newell Teapot",
        base_dir=BASE_DIR,
        glsl_dir=GLSL_DIR,
        data=data,
    )
    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    main()
