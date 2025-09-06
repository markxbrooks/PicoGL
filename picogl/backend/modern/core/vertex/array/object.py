"""
vertex_array_object.py

This module defines the `VertexArrayObject` class, which encapsulates the creation, management,
and usage of OpenGL Vertex Array Objects (VAOs) in modern OpenGL rendering workflows.

The `VertexArrayObject` class inherits from `VertexBuffer` and provides
a clean, object-oriented interface for managing VAO handles and vertex
attribute configurations.

It supports binding/unbinding operations,
attribute registration, and rendering via `glDrawArrays`.

Features:
- Automatic VAO generation if none is provided
- Storage and enabling of vertex attribute definitions
- Integration with VBOs via `ModernVBO` (used as context managers)
- Simplified draw calls for points or other primitive modes
- Graceful deletion and handle management

Dependencies:
- numpy
- PyOpenGL (OpenGL.GL and OpenGL.raw.GL)

Example usage:
==============
>>>vao = VertexArrayObject()
...vao.add_attribute(index=0, vbo=vbo, size=3)
...vao.add_attribute(index=1, vbo=colors, size=3)
...vao.update(index_count=100)

Intended for OpenGL 3.0+ with VAO support.

"""

import ctypes
from typing import Optional

import numpy as np
from OpenGL.GL import glDeleteVertexArrays, glGenVertexArrays
from OpenGL.raw.GL._types import GL_FLOAT, GL_UNSIGNED_INT
from OpenGL.raw.GL.ARB.vertex_array_object import glBindVertexArray
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays
from OpenGL.raw.GL.VERSION.GL_1_5 import (
    GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    glBindBuffer,
)
from OpenGL.raw.GL.VERSION.GL_2_0 import (
    glEnableVertexAttribArray,
    glVertexAttribPointer,
)

from picogl.backend.modern.core.vertex.array.helpers import (
    enable_points_rendering_state,
)
from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer
from picogl.buffers.vertex.aliases import NAME_ALIASES
from picogl.logger import Logger as log
from picogl.safe import gl_gen_safe


class VertexArrayObject(VertexBase):
    """
    OpenGL Vertex Array Objects (VAO) class
    """

    def __init__(self, handle: int = None):
        """
        VertexArrayObject

        :param handle: int Handle (ID) of the OpenGL Vertex Array Object (VAO).
        """
        self._configured: bool = False
        if not handle or handle is None:
            if glGenVertexArrays:
                handle = gl_gen_safe(glGenVertexArrays)
            else:
                raise RuntimeError(
                    "glGenVertexArrays not available — OpenGL context not ready"
                )
        super().__init__(handle)
        self.attributes = []
        self.vbos = []
        self.named_vbos: dict[str, VertexBuffer] = {}
        self.vao = None  # Bonds Vertex Array Object. Does absolutely nothing
        self.vbo = None  # Atom Vertex Buffer Object
        self.cbo = None  # Color Vertex Buffer Object
        self.nbo = None  # Normal Vertex Buffer Object
        self.ebo = None  # Bond Index Buffer Object
        # self.named_vbos: dict[str, LegacyVBO] = {}  # store by semantic name
        self.ebo = None
        self.ebo = None
        self.layout: Optional[LayoutDescriptor] = None
        # self.named_vbos: dict[str, ModernVBO] = {}  # store by semantic name
        self.bind()

    def bind(self):
        """
        Bind the VAO for use in rendering.
        """
        glBindVertexArray(self.handle)

    def unbind(self):
        """
        Unbind the VAO by binding to zero.
        """
        glBindVertexArray(0)

    def delete(self):
        """
        Delete the VAO from GPU memory.
        """
        glDeleteVertexArrays(1, [self.handle])

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """
        set_layout

        :param layout: LayoutDescriptor: The layout descriptor to define the vertex attribute format.
        :raises: None

        Sets the layout for the rendering setup by binding the buffers and configuring the attributes.
        The state is stored in the Vertex Array Object (VAO). This method assumes a single Vertex Buffer
        Object (VBO) holds all position data but can be adapted as required. Handles optional usage of
        Normal Buffer Object (NBO) and Element Buffer Object (EBO) if present.
        """
        try:
            self.layout = layout
            if self.vao is None:
                return
            glBindVertexArray(self.handle)

            if self.vbo is not None:
                glBindBuffer(GL_ARRAY_BUFFER, getattr(self.vbo, "_id", self.vbo))
            if self.nbo is not None:
                # If you have multiple buffers, bind as needed per attribute
                pass  # adapt as needed

            if self.layout:
                for attr in self.layout.attributes:
                    log.parameter("attr", attr)
                    glEnableVertexAttribArray(attr.index)
                    glVertexAttribPointer(
                        attr.index,
                        attr.size,
                        attr.type,
                        attr.normalized,
                        attr.stride,
                        ctypes.c_void_p(attr.offset),
                    )
            if self.ebo is not None:
                glBindBuffer(
                    GL_ELEMENT_ARRAY_BUFFER, getattr(self.ebo, "_id", self.ebo)
                )

            glBindVertexArray(0)
            self._configured = True
        except Exception as ex:
            log.error(f"error {ex} occurred setting layout")

    def add_vbo_object(self, name: str, vbo: "LegacyVBO") -> "LegacyVBO":
        """Register a VBO by semantic name or shorthand alias."""
        # normalize to canonical key
        canonical = NAME_ALIASES.get(name, name)

        # store consistently
        self.named_vbos[canonical] = vbo

        # and assign to attribute if it exists
        if hasattr(self, canonical):
            setattr(self, canonical, vbo)

        return vbo

    def get_vbo_object(self, name: str) -> "LegacyVBO":
        """Retrieve a VBO by its semantic or shorthand name."""
        canonical = NAME_ALIASES.get(name, name)
        return self.named_vbos.get(canonical)

    def add_vbo(
        self,
        index: int,
        data: np.ndarray,
        size: int,
        dtype: int = GL_FLOAT,
        name: str = None,
        handle: int = None,
    ) -> ModernVBO:
        """
        Add a Vertex Buffer Object (VBO) to the VAO and set its attributes.

        :param handle:
        :param index: VAO attribute index
        :param data: Vertex data
        :param size: Size per vertex (e.g., 3 for vec3)
        :param dtype: OpenGL data type (e.g., GL_FLOAT)
        :param name: Optional semantic name (e.g., "position", "color")
        :return: OpenGL buffer handle (GLuint)
        """
        vbo = ModernVBO(handle=handle)
        vbo.bind()
        vbo.set_data(data)
        vbo.set_vertex_attributes(index=index, data=data, size=size, dtype=dtype)
        vbo.configure()
        self.attributes.append((index, vbo.handle, size, dtype, False, 0, 0))
        self.vbos.append(vbo)
        if name:
            self.named_vbos[name] = vbo
        return vbo

    def delete_buffers(self):
        """
        delete_buffers

        :return: None
        """
        for vbo in self.vbos:
            delete_buffer(vbo)
        self.vbos.clear()

        if self.ebo:
            delete_buffer(self.ebo)
            self.ebo = None

        self.named_vbos.clear()

    def add_attribute(
        self,
        index: int,
        vbo: int,
        size: int = 3,
        dtype: int = GL_FLOAT,
        normalized: bool = False,
        stride: int = 0,
        offset: int = 0,
    ):
        """
        add_attribute

        :param index: int Index of the vertex attribute.
        :param vbo: int Vertex Buffer Object (VBO) associated with this attribute.
        :param size: int Size of the vertex attribute (e.g., 3 for a 3D vector).
        :param dtype: int Data type of the vertex attribute (default is GL_FLOAT).
        :param normalized: bool Whether the data is normalized (default is False).
        :param stride: int Byte offset between consecutive vertex attributes (default is 0).
        :param offset: int Byte offset to the first component of the
        vertex attribute (default is 0).
        Add a vertex attribute to the VAO.
        """
        self.attributes.append((index, vbo, size, dtype, normalized, stride, offset))

    def add_ebo(self, data: np.ndarray) -> ModernEBO:
        """
        add_ebo

        :param data: np.ndarray
        :return: int
        """
        ebo = ModernEBO(data=data)
        ebo.bind()
        ebo.set_element_attributes(data=data, size=data.nbytes, dtype=GL_STATIC_DRAW)
        ebo.configure()
        self.ebo = ebo
        return ebo

    def set_ebo(self, ebo: int) -> int:
        """
        add_ebo

        :param ebo: int
        :return: int
        """
        self.ebo = ModernEBO(handle=ebo)
        self.ebo.bind()
        return ebo

    @property
    def index_count(self) -> str | int | None:
        """
        Return the number of indices in the EBO.

        :return: int
        """
        try:
            if self.ebo:
                if hasattr(self.ebo, "data"):
                    return len(self.ebo.data)
            return 0
        except Exception as ex:
            log.error(f"error {ex} occurred")

    def draw(
        self,
        index_count: int = None,
        dtype: int = GL_UNSIGNED_INT,
        mode: int = GL_POINTS,
        pointer: int = ctypes.c_void_p(0),
    ):
        """
        draw

        :param pointer: ctypes.c_void_p(0)
        :param dtype: GL_UNSIGNED_INT
        :param index_count: int Number of vertices to draw.
        :param mode: int e.g. GL_POINT
        :return: None
        """
        atom_count = index_count or self.index_count
        if mode == GL_POINTS:
            enable_points_rendering_state()
        if self.ebo:
            glDrawElements(mode, atom_count, dtype, pointer)
        else:
            glDrawArrays(mode, 0, atom_count)
