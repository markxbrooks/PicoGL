"""
A module for OpenGL framebuffer readback operations.

This module provides functionalities for reading pixel and depth values
from the OpenGL framebuffer using the `glReadPixels` function. It supports
depth component sampling and utility methods for acquiring data.

Classes:
- GLReadback: Provides static and instance methods for reading depth data.

"""

from typing import Any

from numpy import dtype, generic, ndarray
from OpenGL.GL import glReadPixels
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_DEPTH_COMPONENT, GL_FLOAT


class GLReadback:
    """GL Readback class"""

    @staticmethod
    def read_depth(x, y, w, h):
        return glReadPixels(x, y, w, h, GL_DEPTH_COMPONENT, GL_FLOAT)

    def read_pixels(
        self,
        depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]],
        x: int,
        y_gl: int,
    ):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)
