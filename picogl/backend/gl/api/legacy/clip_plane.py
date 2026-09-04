"""Legacy clipping plane wrappers."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glClipPlane

from picogl.backend.gl.enums.legacy import GLLegacyClipPlane


def gl_clip_plane(plane: GLLegacyClipPlane, equation: Sequence[float]) -> None:
    """Define a clipping plane equation (a, b, c, d)."""
    # glClipPlane expects GLdouble[4]; callers often pass float32 arrays.
    coeffs = np.asarray(equation, dtype=np.float64).reshape(4)
    glClipPlane(int(plane), coeffs)
