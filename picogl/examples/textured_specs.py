"""Pre-built TexturedRendererSpec values for tutorial examples."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable

"""from examples.tu04 import _TU04_MESH
from examples.tu_02_texture_without_normal import CUBE_SPEC"""
from picogl.examples.data.cube_data import g_uv_buffer_data, g_vertex_buffer_data
from picogl.utils.mesh.cube_mesh import CubeMesh
from picogl.utils.mesh.object_mesh import MeshObject
from picogl.utils.mesh.protocol import MeshProtocol

_EXAMPLES_DIR = Path(__file__).resolve().parent

_TEAPOT_MESH = _EXAMPLES_DIR / "data" / "teapot2.obj"


def create_cube_mesh(flip_v: bool) -> CubeMesh:
    mesh = CubeMesh(g_vertex_buffer_data, g_uv_buffer_data)
    if flip_v:
        mesh.with_flipped_v()
    return mesh


def create_teapot_mesh(flip_v: bool) -> MeshObject:
    return MeshObject(_TEAPOT_MESH).get_mesh(flip_v=flip_v)


def obj_mesh_factory(path: Path | str) -> Callable[[bool], MeshProtocol]:
    """Named mesh factory for any indexed OBJ (position + UV, tu02/tu04 shaders)."""

    obj_path = Path(path)

    def create_mesh(flip_v: bool) -> MeshObject:
        return MeshObject(obj_path).get_mesh(flip_v=flip_v)

    return create_mesh
