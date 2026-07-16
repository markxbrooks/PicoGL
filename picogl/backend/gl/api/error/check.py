"""
Error checking
"""

from __future__ import annotations

from decologr import Decologr as log
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_NO_ERROR, glGetError
from OpenGL.raw.GLU import gluErrorString

# Re-export for callers that must not import OpenGL directly.
__all__ = [
    "GL_NO_ERROR",
    "check_error_after",
    "gl_check_error",
    "gl_check_errors",
    "gl_get_error",
    "glu_error_string",
]


def glu_error_string(error: int) -> bytes | str:
    """Return a human-readable description of an OpenGL error code."""
    return gluErrorString(error)


def gl_check_errors():
    """
    check_errors

    :return:
    """
    error = glGetError()
    if error != GL_NO_ERROR:
        log.message(f"GL ERROR: {gluErrorString(error)}")


def check_error_after(label: str = "") -> None:
    """
    check_error_after

    :param label: str
    :return: None
    """
    err = glGetError()
    if err != GL_NO_ERROR:
        log.error(f"⚠️ OpenGL error after {label}: {err}")


def gl_check_error(chain_id: str = ""):
    """gl_check_error"""
    err = glGetError()
    if err != GL_NO_ERROR:
        log.warning(f"⚠️ GL error after VAO setup for chain {chain_id}: {err}")


def gl_get_error():
    """gl get error"""
    return glGetError()
