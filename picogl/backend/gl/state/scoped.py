"""State-preserving context managers for temporary OpenGL capability changes."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from picogl.backend.gl.api.enable import (
    GLCapabilities,
    gl_disable,
    gl_enable,
    gl_is_enabled,
)


@contextmanager
def gl_capability(capability: GLCapabilities, enabled: bool) -> Iterator[None]:
    """Temporarily set an OpenGL capability and restore the previous state on exit."""
    was_enabled = bool(gl_is_enabled(capability))
    if enabled:
        gl_enable(capability)
    else:
        gl_disable(capability)
    try:
        yield
    finally:
        if was_enabled:
            gl_enable(capability)
        else:
            gl_disable(capability)


@contextmanager
def disabled(capability: GLCapabilities) -> Iterator[None]:
    """Temporarily disable an OpenGL capability and restore the previous state on exit."""
    with gl_capability(capability, False):
        yield


@contextmanager
def enabled(capability: GLCapabilities) -> Iterator[None]:
    """Temporarily enable an OpenGL capability and restore the previous state on exit."""
    with gl_capability(capability, True):
        yield
