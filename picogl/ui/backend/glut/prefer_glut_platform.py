"""Ensure PyOpenGL binds a GLUT/GL stack that creates a usable context.

Import this module **before** ``OpenGL`` / ``OpenGL.GLUT``:

- macOS: prefer Apple GLUT.framework over Homebrew freeglut
- Linux: prefer GLX over EGL (Wayland + freeglut mismatch)
"""

from __future__ import annotations

import picogl.ui.backend.glut.prefer_apple_glut  # noqa: F401
import picogl.ui.backend.glut.prefer_glx  # noqa: F401
