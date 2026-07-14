"""
A utility function for retrieving a string describing OpenGL properties.

This function provides a way to query specific properties about the
OpenGL implementation currently in use by the application. It delegates
the query to OpenGL's ``glGetString`` function and returns its result.

Named ``get_string`` (not ``string``) so that putting ``picogl/.../gl/api`` on
``sys.path`` does not shadow the Python standard-library ``string`` module
(that break circularly initializes ``logging`` via PySide/Shiboken).
"""

from typing import Any

from OpenGL.GL import glGetString


def gl_get_string(param) -> Any:
    return glGetString(param)
