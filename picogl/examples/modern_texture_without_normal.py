"""
Tutorial 02 — Textured cube (no normals).

Left-drag rotates, wheel zooms, R resets.
"""

from __future__ import annotations

import os
import sys

from picogl.examples.modern_simple_textured_teapot import (_TU02_GLSL,
                                                           _TU02_TEXTURE)

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_apple_glut  # noqa: F401
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.textured_specs import create_cube_mesh
from picogl.ui.backend.glut.window.textured_mesh import (TexturedMeshRenderer,
                                                         TexturedRendererSpec)

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
if __name__ == "__main__":
    win = TexturedMeshRenderer(CUBE_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()
