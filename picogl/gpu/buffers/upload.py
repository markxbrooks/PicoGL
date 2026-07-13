"""
OpenGL Geometry Buffer Upload
=============================

This module provides utilities for uploading vertex and element data to OpenGL buffers,
including VAOs (Vertex Array Objects), VBOs (Vertex Buffer Objects), and optionally EBOs
(Element Buffer Objects). It supports interleaved vertex attributes and automatic binding
of attribute pointers.

Functions:
----------

.. autofunction:: upload_geometry_buffers
    General-purpose function to upload vertex and optional index data to OpenGL buffers.
    Automatically binds attribute pointers and stores buffer handles in a user-defined object.

.. autofunction:: upload_vertex_buffer
    Uploads a simple vertex buffer and computes proximity-based index pairs for rendering.

Parameters:
-----------
- `vao_target`: Name of the VAO attribute in the target object.
- `vbo_target`: Name of the VBO attribute in the target object.
- `render_buffers`: Object or dataclass holding OpenGL buffer handles.
- `vertex_data`: Interleaved vertex attributes (e.g., positions, normals).
- `attributes`: List of tuples (location, size, offset) for attribute pointers.
- `element_data`: Optional index data for indexed rendering.
- `ebo_target`: Name of the EBO attribute in the target object.
- `usage`: Buffer usage hint (e.g., GL_STATIC_DRAW).

Usage Example:
--------------

.. code-block:: python

    upload_geometry_buffers(
        vao_target="mesh_vao",
        vbo_target="mesh_vbo",
        render_buffers=my_buffers,
        vertex_data=vertices,
        attributes=[(0, 3, 0), (1, 3, 12)],
        element_data=indices,
        ebo_target="mesh_ebo"
    )
"""

import ctypes
from typing import Optional

import numpy as np
from picogl.backend.gl.api import gl_bind_buffer
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.buffer_data import gl_buffer_data
from picogl.backend.gl.api.enable_vertex_array import gl_enable_vertex_array
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer
from picogl.backend.gl.api.vertex.generate_array import \
    gl_generate_vertex_array
from picogl.backend.gl.api.vertex.vertex_array import gl_bind_vertex_array
from picogl.backend.gl.enums import GLBufferTarget, GLNumeric, GLUsageHint
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.boolean import GLBoolean


def upload_geometry_buffers(
    vao_target: str,
    vbo_target: str,
    render_buffers: object,
    vertex_data: np.ndarray,
    attributes: list[tuple[int, int, int]],  # (location, size, offset)
    *,
    element_data: Optional[np.ndarray] = None,
    ebo_target: Optional[str] = None,
    usage: GLUsageHint = GLUsageHint.STATIC_DRAW,
) -> None:
    """
    upload_geometry_buffers

    :param vao_target: Name of the VAO attribute in render_buffers (e.g. "calpha_vao")
    :param vbo_target: Name of the VBO attribute in render_buffers (e.g. "calpha_buffer_group")
    :param render_buffers: Any object or dataclass holding OpenGL buffer handles
    :param vertex_data: Interleaved vertex attributes (e.g. position_array + normal)
    :param attributes: List of tuples (location, size, offset) for glVertexAttribPointer
    :param element_data: Optional index data (e.g. for GL_TRIANGLES)
    :param ebo_target: Name of the EBO attribute in render_buffers
    :param usage: GL_STATIC_DRAW or GL_DYNAMIC_DRAW

    General-purpose VAO/VBO upload function for vertex meshdata.
    """

    vao = gl_generate_vertex_array(1)
    vao_object = VertexArrayObject()
    vbo = gl_generate_buffers(1)
    vao_object.add_vbo(index=0, data=vertex_data, size=3, name=vbo_target)

    setattr(render_buffers, vao_target, vao)
    setattr(render_buffers, vbo_target, vbo)

    gl_bind_vertex_array(vao)
    gl_bind_buffer(GLBufferTarget.ARRAY, vbo)
    gl_buffer_data(
        target=GLBufferTarget.ARRAY,
        size=vertex_data.nbytes,
        data=vertex_data,
        usage_hint=usage,
    )

    stride = vertex_data.shape[1] * 4  # float32 = 4 bytes

    for location, size, offset in attributes:
        gl_enable_vertex_array(location)
        gl_vertex_attrib_pointer(
            location,
            size,
            GLNumeric.FLOAT,
            GLBoolean.FALSE,
            stride,
            ctypes.c_void_p(offset),
        )

    if element_data is not None and ebo_target is not None:
        ebo = gl_generate_buffers(1)
        setattr(render_buffers, ebo_target, ebo)
        gl_bind_buffer(GLBufferTarget.ELEMENT, ebo)
        gl_buffer_data(
            target=GLBufferTarget.ELEMENT,
            size=element_data.nbytes,
            data=element_data,
            usage_hint=usage,
        )

    gl_bind_vertex_array(0)


def upload_vertex_buffer(vao: int, vbo: int, points: np.ndarray):
    """
    upload_vertex_buffer

    :param vao: int
    :param vbo: int
    :param points: np.ndarray
    :return: list indices
    """
    gl_bind_vertex_array(vao)
    gl_bind_buffer(GLBufferTarget.ARRAY, vbo)
    gl_buffer_data(
        target=GLBufferTarget.ARRAY,
        size=points.nbytes,
        data=points,
        usage_hint=GLUsageHint.STATIC_DRAW,
    )
    gl_enable_vertex_array(0)
    gl_vertex_attrib_pointer(
        index=0,
        size=3,
        num_type=GLNumeric.FLOAT,
        normalized=GLBoolean.FALSE,
        stride=0,
        offset=None,
    )
    gl_bind_vertex_array(0)
