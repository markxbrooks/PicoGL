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
- PyOpenGL (OpenGL.gl and OpenGL.raw.gl)

Example usage:
==============
>>> vao = VertexArrayObject()
>>> vao.add_attribute(index=0, vertices=vertices, size=3)
>>> vao.add_attribute(index=1, vertices=colors, size=3)
>>> vao.update(index_count=100)

Intended for OpenGL 3.0+ with VAO support.

"""

import ctypes
from contextlib import contextmanager
from typing import Optional, Union

import numpy as np
from decologr import Decologr as log
from picogl.backend.gl.enums import (
    GLBufferTarget,
    GLDrawMode,
    GLIndexType,
    GLNumeric,
    GLUsageHint,
)
from picogl.backend.gl.resource import GLResource
from picogl.backend.gl.wrappers import gl_draw_arrays, gl_draw_elements
from picogl.backend.gl.wrappers.buffer import gl_bind_buffer, gl_buffer_subdata
from picogl.backend.gl.wrappers.enable_vertex_array import gl_enable_vertex_array
from picogl.backend.gl.wrappers.glcleanup import (
    gl_delete_buffers,
    gl_delete_vertex_arrays,
)
from picogl.backend.gl.wrappers.vertex_array import (
    gl_bind_vertex_array,
    gl_gen_vertex_arrays,
    gl_is_vertex_array,
)
from picogl.backend.gl.wrappers.vertex_attrib_pointer import gl_vertex_attrib_pointer
from picogl.backend.modern.core.vertex.array.helpers import (
    enable_points_rendering_state,
)
from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.gpu.buffers.attributes import LayoutDescriptor
from picogl.gpu.buffers.base import VertexBase
from picogl.gpu.buffers.vertex.aliases import NAME_ALIASES
from picogl.safe import gl_gen_safe
from PySide6.QtGui import QOpenGLContext

from elmo.log.silence import SILENT_VAO


class VertexArrayObject(VertexBase, GLResource):
    """
    OpenGL Vertex Array Objects (VAO) class
    """

    def __init__(self, handle: int = None, *, registry_label: Optional[str] = None):
        """
        VertexArrayObject

        :param handle: int Handle (ID) of the OpenGL Vertex Array Object (VAO).
        :param registry_label: Optional custom label for :func:`store_in_gl_registry`
            (defaults to ``self.__class__.__name__``).
        """
        self._creation_context = QOpenGLContext.currentContext()
        log.message(
            f"VAO context :{id(self._creation_context)}",
            scope="VertexArrayObject",
            silent=SILENT_VAO,
        )
        self._registry_label = registry_label
        self._configured: bool = False
        if not handle or handle is None:
            if gl_gen_vertex_arrays():
                handle = gl_gen_safe(gl_gen_vertex_arrays())
            else:
                raise RuntimeError(
                    "glGenVertexArrays not available — OpenGL context not ready"
                )
        super().__init__(handle)
        self.attributes = []
        self.vbos = []
        self.named_vbos: dict[str, VertexBuffer] = {}
        self.vao: Optional[int] = (
            None  # Bonds Vertex Array Object. Does absolutely nothing
        )
        self.ebo = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None
        self.bind()

    def is_valid_in_current_context(self) -> bool:
        ctx = QOpenGLContext.currentContext()

        if ctx is None:
            return False

        # Fast path: correct context
        if ctx is self.context:
            return True

        # Optional fallback: gl-level validation (ONLY if sharing contexts exist)
        try:
            handle = getattr(self, "handle", None)
            if handle:
                return bool(gl_is_vertex_array(handle))
        except Exception:
            return False

        return False

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """configure"""
        """if self._configured:
            return"""

        if self.handle is None:
            return

        with self.bind():

            self.layout = layout

            if self.ebo:
                gl_bind_buffer(GLBufferTarget.ELEMENT, self.ebo.handle)

            # Configure attributes
            for attr in layout.attributes:
                vbo = self.get_vbo_object(attr.name)  # <-- CRITICAL

                if vbo is None:
                    raise RuntimeError(f"No VBO bound for attribute '{attr.name}'")

                vbo.bind()  # <-- THIS IS THE FIX
                gl_enable_vertex_array(attr.index)
                gl_vertex_attrib_pointer(
                    index=attr.index,
                    size=attr.size,
                    num_type=attr.type,
                    normalized=attr.normalized,
                    stride=attr.stride,
                    offset=attr.offset,
                )

            gl_bind_vertex_array(0)
            self._configured = True

    @contextmanager
    def bound(self):
        if not self.bind():
            raise RuntimeError("Failed to bind VAO")
        try:
            yield
        finally:
            gl_bind_vertex_array(0)

    def bind(self) -> Union["VertexArrayObject", None]:
        """
        Bind the VAO for use in rendering.
        :return: True if bound, False if skipped (wrong context — avoids GL_INVALID_OPERATION/segfault).
        """
        if not self.is_valid_in_current_context():
            log.error(
                "VAO created in different gl context; skipping bind to avoid invalid operation",
                scope=self.__class__.__name__,
            )
            return None
        gl_bind_vertex_array(self.handle)
        return self

    def unbind(self):
        """
        Unbind the VAO by binding to zero.
        """
        gl_bind_vertex_array(0)

    def delete(self):
        """
        Delete the VAO from GPU memory.
        """
        gl_delete_vertex_arrays(1, [self.handle])

    def configure(self):
        """set layout"""
        self.set_layout(self.layout)

    def add_vbo_object(self, name: str, vbo: "ModernVBO") -> "ModernVBO":
        """Register a VBO by semantic name or shorthand alias."""
        # normalize to canonical key
        canonical = NAME_ALIASES.get(name, name)
        if not isinstance(vbo, VertexBuffer):
            raise TypeError(f"Expected VertexBuffer, got {type(vbo)}")

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

    def add_vbo_data(
        self,
        data: np.ndarray,
        index: int = 0,
        size: int = 3,
        dtype: int = GLNumeric.FLOAT,
        name: str = None,
        handle: int = None,
    ) -> ModernVBO:
        """
        Add VBO data to this VAO.

        Compatibility wrapper for older callers that only supplied vertex data.
        """
        return self.add_vbo(
            index=index,
            data=data,
            size=size,
            dtype=dtype,
            name=name,
            handle=handle,
        )

    def add_vbo(
        self,
        index: int,
        data: np.ndarray,
        size: int,
        dtype: int = GLNumeric.FLOAT,
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
            gl_delete_buffers(vbo)
        self.vbos.clear()

        if self.ebo:
            gl_delete_buffers(self.ebo)
            self.ebo = None

        self.named_vbos.clear()

    def add_attribute(
        self,
        index: int,
        vbo: int,
        size: int = 3,
        dtype: int = GLNumeric.FLOAT,
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
        # EBO association is stored on the *currently bound* VAO. ``__init__`` ends
        # with ``bind()``, but callers may have unbound since then — re-bind here.
        if not self.bind():
            raise RuntimeError(
                "add_ebo: VAO is not valid in the current OpenGL context"
            )
        ebo = ModernEBO(data=data)
        ebo.bind()
        ebo.set_element_attributes(
            data=data, size=data.nbytes, dtype=GLUsageHint.STATIC_DRAW
        )
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
        dtype: int = GLIndexType.UNSIGNED_INT,
        mode: int = GLDrawMode.POINTS,
        pointer: Union[int, ctypes.c_void_p, None] = ctypes.c_void_p(0),
        first: int = 0,
    ):
        """
        draw

        :param pointer: ctypes.c_void_p(0)
        :param dtype: GL_UNSIGNED_INT
        :param index_count: int Number of vertices to draw.
        :param mode: int e.g. GL_POINT
        :param first: First vertex for non-indexed draws.
        :return: None
        """
        atom_count = index_count or self.index_count
        if mode == GLDrawMode.POINTS:
            enable_points_rendering_state()
        try:
            if not self.bind():
                return
            if index_count is None:
                index_count = self.index_count
            if index_count == 0:
                self.unbind()
                return
            if self.ebo:
                # Re-bind EBO: if it was not captured into this VAO at creation time,
                # glDrawElements can use a stale global EBO (e.g. from bond draws) and
                # produce fan/spike artefacts on indexed meshes such as ribbons.
                self.ebo.bind()
                gl_draw_elements(atom_count, dtype, mode, pointer=pointer)
            else:
                gl_draw_arrays(atom_count, mode, first=int(first))
        finally:
            self.unbind()

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
                gl_buffer_subdata(GLBufferTarget.ARRAY, 0, arr.nbytes, arr)
            else:
                vbo.set_data(arr)
        finally:
            gl_bind_buffer(GLBufferTarget.ARRAY, 0)
            self.unbind()
