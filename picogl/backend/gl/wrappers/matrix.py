from __future__ import annotations

from typing import Optional

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glMatrixMode
from pyglm import glm

from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode


def gl_matrix_mode(mode: GLLegacyMatrixMode):
    glMatrixMode(mode)


def gl_load_matrixf(m: Optional[np.ndarray, glm.mat4]):
    """gl load matrix"""
    glLoadMatrixf(m)