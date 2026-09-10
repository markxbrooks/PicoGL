"""
gl enable / disable / is-enabled helpers.
"""

from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled

from picogl.backend.gl.api.capabilities import GLCapabilities

__all__ = [
    "GLCapabilities",
    "gl_disable",
    "gl_disable_capability_list",
    "gl_enable",
    "gl_enable_capability_list",
    "gl_is_enabled",
    "toggle_capability",
]


def gl_enable(cap: GLCapabilities) -> None:
    """Enable an OpenGL capability."""
    glEnable(cap)


def gl_enable_capability_list(capabilities: list[GLCapabilities]) -> None:
    """Enable each capability in *capabilities*."""
    for cap in capabilities:
        gl_enable(cap)


def gl_disable(cap: GLCapabilities) -> None:
    """Disable an OpenGL capability."""
    glDisable(cap)


def gl_disable_capability_list(capabilities: list[GLCapabilities]) -> None:
    """Disable each capability in *capabilities*."""
    for cap in capabilities:
        gl_disable(cap)


def gl_is_enabled(cap: GLCapabilities) -> bool:
    """Return whether *cap* is currently enabled."""
    return bool(glIsEnabled(cap))


def toggle_capability(enabled: bool, capability: GLCapabilities) -> None:
    """Enable or disable *capability* based on *enabled*."""
    if enabled:
        gl_enable(capability)
    else:
        gl_disable(capability)
