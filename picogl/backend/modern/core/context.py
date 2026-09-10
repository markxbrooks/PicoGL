"""Tu02 textured-cube demo — delegates to TexturedMeshRenderer."""

from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

from examples.tu_02_texture_without_normal import CUBE_SPEC

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.ui.backend.glut.window.textured_mesh import TexturedMeshRenderer

if __name__ == "__main__":
    win = TexturedMeshRenderer(CUBE_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()
