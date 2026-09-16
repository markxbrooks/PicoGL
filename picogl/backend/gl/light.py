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
    """
    Represents a light source in an OpenGL application.

    This class provides functionality to control OpenGL fixed-function pipeline
    lighting properties. It includes methods for configuring specific lighting
    parameters such as diffuse, ambient, or specular components using OpenGL
    functions.

    Methods:
        lightf: Sets the specified lighting parameter using OpenGL's glLightfv
                function.
    """

    @staticmethod
    def lightf(
        light: GLFixedFunctionCapability,
        pname: GLLightParameter = GLLightParameter.DIFFUSE,
        params: Sequence[float] = None,
    ):
        """
        Sets the parameters for a light source in OpenGL fixed-function pipeline.

        The function sets specific parameters for a given light source by calling the
        OpenGL `glLightfv` function.

        Args:
            light: The light source identifier as a `GLFixedFunctionCapability`.
            pname: The light's parameter to be set, specified as a
                `GLLightParameter`. Defaults to `GLLightParameter.DIFFUSE`.
            params: A sequence of floats representing the values of the parameter
                being set. Defaults to None.

        """
        glLightfv(light, pname, params)
