"""
This module provides an implementation for controlling OpenGL light sources using
the GLFixedFunctionCapability and GLLightParameter enumerations.

It includes a utility static method to configure light properties via OpenGL functions.
"""

from typing import Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import glLightfv
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLLightParameter


class GLLightSource:

    @staticmethod
    def lightf(
        light: GLFixedFunctionCapability,
        pname: GLLightParameter = GLLightParameter.DIFFUSE,
        params: Sequence[float] = None,
    ):
        glLightfv(light, pname, params)
