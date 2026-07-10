"""
A utility function for retrieving a string describing OpenGL properties.

This function provides a way to query specific properties about the
OpenGL implementation currently in use by the application. It delegates
the query to OpenGL's `glGetString` function and returns its result.

Parameters
----------
param : Any
    The OpenGL identifier for the property to query.

Returns
-------
Any
    The string value of the requested OpenGL property.
"""

from typing import Any

from OpenGL.GL import glGetString


def gl_get_string(param) -> Any:
    return glGetString(param)
