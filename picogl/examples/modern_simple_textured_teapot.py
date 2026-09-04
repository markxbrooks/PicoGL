"""
Simple Textured PicoGL Teapot — position + UV, tu02 flat texture shader.

For Phong-lit texture + vertex-color mixing, use modern_textured_teapot.py (RenderWindow).
"""

from __future__ import annotations

import os
import sys

if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.examples.textured_specs import _EXAMPLES_DIR, create_teapot_mesh
from picogl.ui.backend.glut.window.textured_mesh import (TexturedMeshRenderer,
                                                         TexturedRendererSpec)

# Same assets as CUBE_SPEC; used by examples/modern_texture_example.py (legacy TextureWindow demo).
_TU02_TEXTURE = _EXAMPLES_DIR / "resources" / "tu02" / "uvtemplate.tga"
_TU02_GLSL = _EXAMPLES_DIR / "glsl" / "tu02"
TEAPOT_SPEC = TexturedRendererSpec(
    width=800,
    height=600,
    title="Simple Textured Newell Teapot",
    zoom_distance=5.0,
    distance_threshold=2.0,
    texture_path=_TU02_TEXTURE,
    glsl_dir=_TU02_GLSL,
    create_mesh=create_teapot_mesh,
)


def main() -> None:
    win = TexturedMeshRenderer(TEAPOT_SPEC)
    win.initializeGL()
    win.initialize()
    win.run()


if __name__ == "__main__":
    main()
