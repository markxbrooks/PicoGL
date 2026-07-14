"""
This module provides a wrapper for setting the line width in OpenGL.

The module contains a single function to set the width of lines rendered
using OpenGL, providing a more Pythonic access to the underlying OpenGL
functionality.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glLineWidth


def gl_line_width(line_width: float) -> None:
    """
    Sets the width of rasterized lines for OpenGL rendering.

    The `gl_line_width` function adjusts the thickness of lines drawn in OpenGL
    contexts. This affects the rendering of all future lines after this function
    is executed, until the line width is modified again.

    Parameters:
    line_width: float
        The width to be set for rasterized lines. Values must be positive.
        The specific range and clamping behavior depend on the OpenGL
        implementation.
    """
    glLineWidth(line_width)
