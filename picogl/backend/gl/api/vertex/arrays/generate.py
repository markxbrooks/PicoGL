"""
Provides a wrapper for the OpenGL function glGenVertexArrays.

This module defines a simple function that returns
the OpenGL glGenVertexArrays function or a Callable
that allows for its usage, enabling creation of vertex
array objects. It relies on the PyOpenGL library and
the OpenGL.GL module for implementation.
"""

from typing import Any, Callable

from OpenGL.GL import glGenVertexArrays


def gl_gen_vertex_arrays() -> Callable[..., Any] | Any:
    """
    Returns the glGenVertexArrays function or a callable implementing its behavior.

    This function serves as a proxy to access OpenGL's glGenVertexArrays functionality. It
    can be used to generate one or more vertex array object names.

    Returns:
        Callable[..., Any] | Any: The glGenVertexArrays function or a callable equivalent
        providing its functionality.
    """
    return glGenVertexArrays
