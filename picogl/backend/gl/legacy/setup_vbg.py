"""
Module to handle headless-safe OpenGL vertex buffer group (VBG) management.

This module provides functions and classes to create and manage vertex buffers
in headless and non-headless environments, ensuring compatibility with OpenGL-
based rendering pipelines. It includes utilities to define attribute layouts,
convert data to numpy arrays, and set up vertex buffer groups (VBGs) for use
in rendering workflows.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy as np
from picogl.backend.gl.enums import GLDrawMode
from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType

if TYPE_CHECKING:
    from picogl.renderer.meshdata import MeshData

# Determine headless test environment as early as possible
_HEADLESS = bool(
    os.environ.get("ELMO_TEST_HEADLESS") or os.environ.get("PYTEST_CURRENT_TEST")
)

# Safe PicoGL enums for environments without a GL context
try:  # pragma: no cover
    from picogl.backend.gl.enums import GLDrawMode as _GLDrawMode
    from picogl.backend.gl.enums import GLNumeric as _GLNumeric

    GL_FLOAT = _GLNumeric.FLOAT
    GL_LINE_STRIP = _GLDrawMode.LINE_STRIP
    GL_TRIANGLE_STRIP = _GLDrawMode.TRIANGLE_STRIP
except Exception:  # pragma: no cover - fallback constants for tests
    GL_FLOAT = 0x1406
    GL_LINE_STRIP = 0x0003
    GL_TRIANGLE_STRIP = 0x0005

# In headless mode, avoid importing PicoGL modules that may touch OpenGL.
if _HEADLESS:
    from picogl.gpu.buffers.vertex.aliases import NAME_ALIASES

    class AttributeSpec:
        def __init__(
            self,
            name: str,
            index: int,
            size: int,
            dtype: int,
            normalized: bool,
            stride: int,
            offset: int,
            role: VertexBufferRole = VertexBufferRole.VBO,
        ):
            self.name = name
            self.index = index
            self.size = size
            self.dtype = dtype
            self.normalized = normalized
            self.stride = stride
            self.offset = offset
            self.role = role

    def legacy_attribute_spec(
        role: VertexBufferRole,
        index: int,
        *,
        size: int = 3,
        name: str | VertexBufferRole | None = None,
        type: int,
        normalized: bool = False,
        stride: int = 0,
        offset: int = 0,
    ) -> AttributeSpec:
        return AttributeSpec(
            name if name is not None else role,
            index,
            size,
            type,
            normalized,
            stride,
            offset,
            role,
        )

    class LayoutDescriptor:
        def __init__(self, specs):
            self.specs = specs

    class _DummyVBO:
        def __init__(self, array: np.ndarray):
            self.data = array

    class VertexBufferGroup:
        def __init__(self, draw_mode: int = GL_TRIANGLE_STRIP):
            self.draw_mode = draw_mode
            self.named_vbos = {}
            self._layout = None

        def add_vbo(self, name: str, array: np.ndarray, size: int = 3):
            self.named_vbos[name] = _DummyVBO(array)

        def set_layout(self, layout: LayoutDescriptor):
            self._layout = layout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def draw(self, index_count: int):
            return None

        def delete(self):
            self.named_vbos.clear()

else:
    from picogl.gpu.buffers.attributes import (
        AttributeSpec,
        LayoutDescriptor,
        legacy_attribute_spec,
    )
    from picogl.gpu.buffers.vertex.aliases import NAME_ALIASES
    from picogl.gpu.buffers.vertex.legacy import VertexBufferGroup as VertexBufferGroup

# VertexBufferGroup is defined above based on _HEADLESS


def build_legacy_vbg_layout(
    positions_size: int = 3,
    normals_size: int = 3,
    colors_size: int = 3,
) -> LayoutDescriptor:
    """
    Headless-safe triple layout (VBO / NBO / CBO). Prefer this from code that imports
    ``setup_vbg`` stubs; use ``build_legacy_layout`` from ``legacy.layout`` elsewhere.
    """
    if _HEADLESS:
        return LayoutDescriptor(
            [
                legacy_attribute_spec(
                    VertexBufferRole.VBO,
                    0,
                    size=positions_size,
                    type=GL_FLOAT,
                ),
                legacy_attribute_spec(
                    VertexBufferRole.NBO,
                    1,
                    size=normals_size,
                    type=GL_FLOAT,
                ),
                legacy_attribute_spec(
                    VertexBufferRole.CBO,
                    2,
                    size=colors_size,
                    type=GL_FLOAT,
                ),
            ]
        )
    from elmo.gl.layout import build_legacy_layout

    return build_legacy_layout(
        positions_size=positions_size,
        normals_size=normals_size,
        colors_size=colors_size,
    )


def build_legacy_vbg_position_layout(component_size: int = 3) -> LayoutDescriptor:
    """Single position attribute at location 0 (e.g. line-strip outline)."""
    if _HEADLESS:
        return LayoutDescriptor(
            [
                legacy_attribute_spec(
                    VertexBufferRole.VBO,
                    0,
                    size=component_size,
                    type=GL_FLOAT,
                ),
            ]
        )
    from elmo.gl.layout import build_legacy_position_only_layout

    return build_legacy_position_only_layout(component_size)


def convert_to_numpy(colors, normals, positions):
    """convert_to_numpy"""
    positions_np = np.array(positions, dtype=np.float32)
    normals_np = np.array(normals, dtype=np.float32)
    colors_np = np.array(colors, dtype=np.float32)
    return colors_np, normals_np, positions_np


def create_vertex_buffer_group(
    draw_mode: int = GL_TRIANGLE_STRIP,
    **attributes,
):
    """
    Create and return a VertexBufferGroup from arbitrary named attributes.

    Parameters
    ----------
    draw_mode : int
        OpenGL draw mode (default: GL_TRIANGLE_STRIP).
    attributes : dict[str, tuple[np.ndarray, int]]
        Named attributes where the key is the buffer name (VBOType.VBO, VBOType.NBO, VBOType.CBO, ...)
        and the value is a tuple of (array, size), where `size` is the number of
        components per vertex (e.g., 2 for UVs, 3 for XYZ, 4 for RGBA).

    Example
    -------
    vbg = create_vertex_buffer_group(
        vertices=(positions, 3),
        nbo=(normals, 3),
        cbo=(colors, 4),  # RGBA colors
    )
    """
    vbg = VertexBufferGroup(draw_mode=draw_mode)
    layout_specs = []

    for index, (name, value) in enumerate(attributes.items()):
        array, size = value
        vbg.add_vbo(name, array, size=size)
        role = NAME_ALIASES.get(name, name)
        if not isinstance(role, VertexBufferRole):
            role = VertexBufferRole.VBO
        layout_specs.append(
            legacy_attribute_spec(
                role,
                index,
                size=size,
                name=NAME_ALIASES.get(name, name),
                type=GL_FLOAT,
            )
        )

    vbg.set_layout(LayoutDescriptor(layout_specs))
    return vbg


def setup_vbg(
    colors: np.ndarray,
    normals: np.ndarray,
    positions: np.ndarray,
    draw_mode: int = GLDrawMode.TRIANGLE_STRIP,
    positions_size: int = 3,
    normals_size: int = 3,
    colors_size: int = 3,
) -> VertexBufferGroup:
    """Create VBO"""
    # ✅ Optional sanity checks
    for name, arr, size in [
        ("positions", positions, positions_size),
        ("normals", normals, normals_size),
        ("colors", colors, colors_size),
    ]:
        if arr.size % size != 0:
            raise ValueError(
                f"{name} array length {arr.size} is not divisible by size={size}"
            )

    vbg = VertexBufferGroup(draw_mode=draw_mode)
    vbg.add_vbo(VBOType.VBO, positions, size=positions_size)
    vbg.add_vbo(VBOType.NBO, normals, size=normals_size)
    vbg.add_vbo(VBOType.CBO, colors, size=colors_size)
    # Set up layout
    layout = build_legacy_vbg_layout(
        positions_size=positions_size,
        normals_size=normals_size,
        colors_size=colors_size,
    )
    vbg.set_layout(layout)
    return vbg


def setup_vbg_from_mesh(
    mesh: MeshData, draw_mode: int = GLDrawMode.TRIANGLE_STRIP
) -> VertexBufferGroup:
    from picogl.gpu.buffers.helper import as_vec3_array

    return setup_vbg(
        colors=as_vec3_array(mesh.colors),
        normals=as_vec3_array(mesh.normals),
        positions=as_vec3_array(mesh.vertices),
        draw_mode=draw_mode,
    )


def setup_position_vbg(positions_np: np.ndarray) -> VertexBufferGroup:
    """setup position vbg"""
    vbg = VertexBufferGroup(draw_mode=GLDrawMode.LINE_STRIP)
    vbg.add_vbo(VBOType.VBO, positions_np, size=3)
    vbg.set_layout(build_legacy_vbg_position_layout())
    return vbg
