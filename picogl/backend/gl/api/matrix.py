"""
This module provides utility functions to interact with OpenGL's matrix mode
and to load matrices using predefined OpenGL methods. It utilizes OpenGL's 1.0
version for matrix operations and maintains compatibility with legacy OpenGL
matrix modes.

Functions in this module include setting the matrix mode and loading a
matrix into the current matrix stack.
"""

from typing import Optional, Union

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import glLoadMatrixf, glMatrixMode
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from pyglm import glm


def gl_matrix_mode(mode: GLLegacyMatrixMode):
    glMatrixMode(mode)


def gl_load_matrixf(matrix: Optional[Union[np.ndarray, glm.mat4]]):
    glLoadMatrixf(matrix)
