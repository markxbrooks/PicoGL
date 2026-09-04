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
    """
    Sets the current matrix mode for subsequent matrix operations.

    This function is used to specify which matrix stack is the target for matrix
    operations such as load, multiply, or push/pop.

    Args:
        mode (GLLegacyMatrixMode): The matrix mode to be set. It specifies whether
        the current matrix stack is the modelview, projection, or texture matrix
        stack.
    """
    glMatrixMode(mode)


def gl_load_matrixf(matrix: Optional[Union[np.ndarray, glm.mat4]]):
    """
    Loads a matrix into the OpenGL matrix stack.

    This function takes a matrix, which can either be a NumPy array or a glm.mat4
    matrix, and loads it into the OpenGL matrix stack using the glLoadMatrixf
    function.

    Parameters:
    matrix (Optional[Union[np.ndarray, glm.mat4]]): The matrix to be loaded into
        the OpenGL matrix stack. This can be a NumPy array or a glm.mat4 matrix.
    """
    glLoadMatrixf(matrix)
