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
from contextlib import contextmanager
from typing import Optional

import numpy as np
from decologr import Decologr as log
from OpenGL.GL import glDeleteVertexArrays, glGenVertexArrays, glBufferSubData
from OpenGL.raw.GL._types import GL_FLOAT, GL_UNSIGNED_INT
from OpenGL.raw.GL.ARB.vertex_array_object import glBindVertexArray
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS
from OpenGL.raw.GL.VERSION.GL_1_1 import glDrawArrays, glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_5 import (GL_ARRAY_BUFFER,
                                          GL_ELEMENT_ARRAY_BUFFER,
                                          GL_STATIC_DRAW, glBindBuffer)
from OpenGL.raw.GL.VERSION.GL_2_0 import (glEnableVertexAttribArray,
                                          glVertexAttribPointer)
from picogl.backend.modern.core.vertex.array.helpers import \
    enable_points_rendering_state
from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer
from picogl.buffers.vertex.aliases import NAME_ALIASES
from picogl.buffers.vertex.registry import store_in_gl_registry
from picogl.safe import gl_gen_safe


def current_gl_context():
    try:
        from PySide6.QtGui import QOpenGLContext
        return QOpenGLContext.currentContext()
    except Exception:
        return None


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
        self.vao: Optional[int] = None  # Bonds Vertex Array Object. Does absolutely nothing
        self.ebo = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None
        self._creation_context_id: Optional[int] = current_gl_context()
        self.bind()

    def is_valid_in_current_context(self) -> bool:
        """True if this VAO was created in the current OpenGL context (safe to bind/draw)."""
        if self._creation_context_id == current_gl_context():
            store_in_gl_registry(self.handle, label=self.__class__.__name__, ctx_id=id(current_gl_context()), buffer_type="VAO")
            return True
        return False

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """configure"""
        if self._configured:
            return

        if self.vao is None:
            return

        if not self.bind():
            raise RuntimeError("Invalid context")

        self.layout = layout

        """# Bind buffers explicitly
        if self.vbo:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo.handle)"""

        if self.ebo:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo.handle)

        # Configure attributes
        for attr in layout.attributes:
            glEnableVertexAttribArray(attr.index)
            glVertexAttribPointer(
                attr.index,
                attr.size,
                attr.type,
                attr.normalized,
                attr.stride,
                ctypes.c_void_p(attr.offset),
            )

        glBindVertexArray(0)
        self._configured = True

    @contextmanager
    def bound(self):
        if not self.bind():
            raise RuntimeError("Failed to bind VAO")
        try:
            yield
        finally:
            glBindVertexArray(0)

    def bind(self) -> bool:
        """
        Bind the VAO for use in rendering.
        :return: True if bound, False if skipped (wrong context — avoids GL_INVALID_OPERATION/segfault).
        """
        if not self.is_valid_in_current_context():
            log.error(
                "VAO created in different GL context; skipping bind to avoid invalid operation",
                scope=self.__class__.__name__,
            )
            return False
        glBindVertexArray(self.handle)
        return True

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

    def configure(self):
        """set layout"""
        self.set_layout(self.layout)

    def add_vbo_object(self, name: str, vbo: "ModernVBO") -> "ModernVBO":
        """Register a VBO by semantic name or shorthand alias."""
        # normalize to canonical key
        canonical = NAME_ALIASES.get(name, name)

        # store consistently
        self.named_vbos[canonical] = vbo

        # and assign to attribute if it exists
        if hasattr(self, canonical):
            setattr(self, canonical, vbo)

        return vbo

    def get_vbo_object(self, name: str) -> VertexBuffer | None:
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
        :param name: Optional semantic name (e.g., "position", "colour")
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

    def _modern_vbo_for_attrib(self, attrib_index: int) -> Optional[ModernVBO]:
        """Return the :class:`ModernVBO` created for ``add_vbo(index=attrib_index, ...)``."""
        for j, attr in enumerate(self.attributes):
            if not attr:
                continue
            if attr[0] == attrib_index and j < len(self.vbos):
                vbo = self.vbos[j]
                if isinstance(vbo, ModernVBO):
                    return vbo
        return None

    def update_vbo(self, index: int, data: np.ndarray) -> None:
        """
        Upload new contents for the vertex buffer tied to attribute ``index``.

        ``index`` is the same value passed to :meth:`add_vbo` (e.g. ``0`` positions,
        ``1`` colours, ``2`` normals). If the new array has the same byte size as
        the existing GPU store, :func:`glBufferSubData` is used; otherwise
        :meth:`ModernVBO.set_data` (``glBufferData``) reallocates the buffer.

        The VAO must have been built via :meth:`add_vbo`; arbitrary
        :meth:`add_attribute` entries (raw handles only) are not updated here.
        """
        if data is None:
            raise TypeError("update_vbo: data must be a numpy array")
        arr = np.ascontiguousarray(np.asarray(data, dtype=np.float32))

        if not self.bind():
            log.error(
                "update_vbo: VAO not valid in current context",
                scope=self.__class__.__name__,
            )
            return

        vbo = self._modern_vbo_for_attrib(index)
        if vbo is None:
            log.warning(
                f"update_vbo: no ModernVBO for attribute index {index}",
                scope=self.__class__.__name__,
            )
            self.unbind()
            return

        try:
            vbo.bind()
            old = getattr(vbo, "data", None)
            if (
                old is not None
                and isinstance(old, np.ndarray)
                and old.dtype == arr.dtype
                and old.nbytes == arr.nbytes
            ):
                glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr)
            else:
                vbo.set_data(arr)
        finally:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            self.unbind()
