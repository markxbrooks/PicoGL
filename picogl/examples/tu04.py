"""
Tutorial 04 — Textured Suzanne (OBJ + DDS).

Left-drag rotates, wheel zooms, R resets.
"""

from __future__ import annotations

import os
import sys



# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from picogl.utils.mesh import MeshObject
from picogl.examples.textured_specs import _EXAMPLES_DIR
from picogl.ui.backend.glut.window.textured_mesh import TexturedRendererSpec
import picogl.ui.backend.glut.prefer_apple_glut  # noqa: F401
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.ui.backend.glut.window.textured_mesh import TexturedMeshRenderer

_TU04_TEXTURE = _EXAMPLES_DIR / "resources" / "tu04" / "uvmap.DDS"
_TU04_GLSL = _EXAMPLES_DIR / "glsl" / "tu04"
_TU04_MESH = _EXAMPLES_DIR / "resources" / "tu04" / "suzanne.obj"

def create_suzanne_mesh(flip_v: bool) -> MeshObject:
    """create Suzanne mesh"""
    return MeshObject(_TU04_MESH).get_mesh(flip_v=flip_v)

SUZANNE_SPEC = TexturedRendererSpec(
    width=400,
    height=300,
    title="Suzanne - Textured Model",
    zoom_distance=5.0,
    distance_threshold=2.0,
    texture_path=_TU04_TEXTURE,
    glsl_dir=_TU04_GLSL,
    create_mesh=create_suzanne_mesh,
    require_texture=False,
)
if __name__ == "__main__":
    win = TexturedMeshRenderer(SUZANNE_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()

