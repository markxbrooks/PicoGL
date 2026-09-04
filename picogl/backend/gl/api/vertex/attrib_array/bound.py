"""Context manager for enabling/disabling vertex attribute arrays."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from picogl.backend.gl.api.vertex.attrib_array.disable import (
    gl_disable_vertex_attrib_array,
)
from picogl.backend.gl.api.vertex.attrib_array.generate import (
    gl_enable_vertex_attrib_array,
)


@contextmanager
def gl_bound_vertex_attrib_arrays(
    vertex_attrib_arrays: list[int],
) -> Iterator[None]:
    """Enable vertex attrib arrays for the block, then disable them."""
    try:
        for vertex_attrib_array in vertex_attrib_arrays:
            gl_enable_vertex_attrib_array(vertex_attrib_array)
        yield
    finally:
        for vertex_attrib_array in reversed(vertex_attrib_arrays):
            gl_disable_vertex_attrib_array(vertex_attrib_array)
