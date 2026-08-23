#!/usr/bin/env python3
"""Legacy PicoGL Cube - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow ``python path/to/legacy_cube_fixed.py`` without installing picogl.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL and then
# fail on glutDisplayFunc with "Attempt to retrieve context when no valid context".
# Must be set before any OpenGL import (including via picogl).
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.backend.glut.glut_renderer import GlutRenderer


class LegacyCubeRenderer(GlutRenderer):
    """Legacy cube renderer using PicoGL LegacyGLMesh (via GlutRenderer)."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy PicoGL Cube",
    ) -> None:
        super().__init__(width=width, height=height, title=title)


def main() -> None:
    """Main function."""
    print("🧪 Legacy PicoGL Cube")
    print("=" * 40)

    if os.environ.get("DISPLAY") is None and os.name != "nt":
        print("❌ No display available. This requires a graphical environment.")
        print("   Try running on a system with X11, Wayland, or macOS display.")
        sys.exit(1)

    try:
        renderer = LegacyCubeRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Cube (OpenGL 1.x/2.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running legacy cube renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   On Linux/Wayland, try: PYOPENGL_PLATFORM=glx python ...")
        print("   On macOS, try running from Terminal.app or iTerm2.")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
