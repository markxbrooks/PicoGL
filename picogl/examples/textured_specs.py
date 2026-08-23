"""Pre-built TexturedRendererSpec values for tutorial examples."""

from __future__ import annotations

from pathlib import Path

from picogl.examples.data.cube_data import g_uv_buffer_data, g_vertex_buffer_data
from picogl.ui.backend.glut.window.textured_mesh import TexturedRendererSpec
from picogl.utils.mesh.cube_mesh import CubeMesh
from picogl.utils.mesh.object_mesh import MeshObject

_EXAMPLES_DIR = Path(__file__).resolve().parent

_TU02_TEXTURE = _EXAMPLES_DIR / "resources" / "tu02" / "uvtemplate.tga"
_TU02_GLSL = _EXAMPLES_DIR / "glsl" / "tu02"

_TU04_MESH = _EXAMPLES_DIR / "resources" / "tu04" / "suzanne.obj"
_TU04_TEXTURE = _EXAMPLES_DIR / "resources" / "tu04" / "uvmap.DDS"
_TU04_GLSL = _EXAMPLES_DIR / "glsl" / "tu04"


def create_cube_mesh(flip_v: bool) -> CubeMesh:
    mesh = CubeMesh(g_vertex_buffer_data, g_uv_buffer_data)
    if flip_v:
        mesh.with_flipped_v()
    return mesh


def create_suzanne_mesh(flip_v: bool) -> MeshObject:
    return MeshObject(_TU04_MESH).get_mesh(flip_v=flip_v)


CUBE_SPEC = TexturedRendererSpec(
    width=800,
    height=600,
    title="Tutorial 02 - Textured Cube",
    zoom_distance=3.0,
    distance_threshold=1.5,
    texture_path=_TU02_TEXTURE,
    glsl_dir=_TU02_GLSL,
    create_mesh=create_cube_mesh,
)

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
