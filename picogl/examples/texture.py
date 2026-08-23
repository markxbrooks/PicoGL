"""
Demonstrating texture — same pipeline as tu_02_texture_without_normal.py.

Uses TexturedMeshRenderer instead of the legacy TextureWindow / TextureRenderer path.
"""

from __future__ import annotations

import os
import sys

from examples.tu_02_texture_without_normal import CUBE_SPEC

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")
from dataclasses import replace
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.ui.backend.glut.window.textured_mesh import TexturedMeshRenderer

# Same assets as CUBE_SPEC; used by examples/texture.py (legacy TextureWindow demo).
TEXTURE_DEMO_SPEC = replace(CUBE_SPEC, title="texture window")

def main() -> None:
    win = TexturedMeshRenderer(TEXTURE_DEMO_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()


if __name__ == "__main__":
    main()
