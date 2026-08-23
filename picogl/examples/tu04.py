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

import picogl.ui.backend.glut.prefer_apple_glut  # noqa: F401
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.textured_specs import SUZANNE_SPEC
from picogl.ui.backend.glut.window.textured_mesh import TexturedMeshRenderer


if __name__ == "__main__":
    win = TexturedMeshRenderer(SUZANNE_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()
