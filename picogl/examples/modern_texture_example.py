"""
Demonstrating texture — MeshData → MeshProtocol → TexturedMeshRenderer.

Same cube assets as tu_02; uses the MeshData adapter instead of CubeMesh.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.data.cube_data import g_uv_buffer_data, g_vertex_buffer_data
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.textured_mesh import (
    TexturedMeshRenderer,
    TexturedRendererSpec,
)
from picogl.utils.mesh import meshdata_factory

_EXAMPLES_DIR = Path(__file__).resolve().parent
_TU02_TEXTURE = _EXAMPLES_DIR / "resources" / "tu02" / "uvtemplate.tga"
_TU02_GLSL = _EXAMPLES_DIR / "glsl" / "tu02"


def main() -> None:
    mesh_data = MeshData.from_raw(vertices=g_vertex_buffer_data, uvs=g_uv_buffer_data)
    spec = TexturedRendererSpec(
        width=800,
        height=600,
        title="texture window (MeshData adapter)",
        zoom_distance=3.0,
        distance_threshold=1.5,
        texture_path=_TU02_TEXTURE,
        glsl_dir=_TU02_GLSL,
        create_mesh=meshdata_factory(mesh_data),
    )
    win = TexturedMeshRenderer(spec)
    win.initializeGL()
    win.initialize()
    win.run()


if __name__ == "__main__":
    main()
