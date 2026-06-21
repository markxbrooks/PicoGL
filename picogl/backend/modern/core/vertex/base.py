"""
vertex_base.py

This module defines the `VertexBuffer` class, a foundational abstraction for
OpenGL objects that require explicit binding and unbinding during rendering.

`VertexBuffer` provides a common interface and context management protocol for derived classes such as
`VertexArrayObject`, `ModernVBO`, and `ModernEBO`.
It ensures consistent handling of OpenGL object lifetimes and usage patterns by enforcing the
implementation of `bind()` and `unbind()` methods.

Features:
- Stores a raw OpenGL object handle (ID)
- Provides `bind()` / `unbind()` interface to be implemented by subclasses
- Supports Python context manager protocol (`with` statement)
- Useful for any OpenGL object that must be bound/unbound during draw calls

Example Usage:
==============
class MyBuffer(VertexBuffer):
...def bind(self): glBindBuffer(GL_ARRAY_BUFFER, self.handle)
...def unbind(self): glBindBuffer(GL_ARRAY_BUFFER, 0)
...
...with MyBuffer(handle) as buf:
...   # buffer is bound
        ...
...# buffer is unbound

Note:
This base class is abstract and cannot be used directly;
`bind` and `unbind` must be implemented in subclasses.

"""

import ctypes

import numpy as np
from OpenGL import error as _gl_err
from OpenGL.raw.GL.VERSION.GL_1_5 import glBufferSubData, glIsBuffer

from picogl.boolean import GLBoolean
from picogl.buffers.base import VertexBase
from picogl.numerical import GLNumeric
from picogl.state.draw_mode import GLBufferTarget, GLIndexType, GLUsageHint
from picogl.wrappers.buffer import gl_bind_buffer
from picogl.wrappers.data import gl_buffer_data
from picogl.wrappers.enable_vertex_array import gl_enable_vertex_array
from picogl.wrappers.vertex_attrib_pointer import gl_vertex_attrib_pointer


class VertexBuffer(VertexBase):
    """
    VertexBuffer
    ============
    Base class for OpenGL vertex-related buffers (VBO, VAO, EBO).

    This handles:
        - Buffer binding/unbinding
        - Data upload (glBufferData)
        - Vertex attribute configuration
        - Type mapping from NumPy dtype to gl constants
    """

    _GL_TYPE_MAP = {
        np.float32: GLNumeric.FLOAT,
        np.uint32: GLIndexType.UNSIGNED_INT,
    }

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GLBufferTarget.ARRAY,
        size: int = 3,
        stride: int = 0,
        dtype: int = GLNumeric.FLOAT,
        index: int = None,
        pointer: ctypes.c_void_p = ctypes.c_void_p(0),
    ):
        super().__init__(handle=handle)
        self.index = index
        self.normalized = False
        self.target = target
        self.components = size
        self.buffer_size = data.nbytes if data is not None else 0
        self.stride = stride
        self.dtype = dtype
        self.pointer = pointer
        self.data = data
        self.offset = 0

    # ----------------------------
    # OpenGL binding / unbinding
    # ----------------------------
    def bind(self) -> None:
        """Bind this buffer."""
        gl_bind_buffer(self.target, self.handle)

    def unbind(self) -> None:
        """Unbind this buffer, ensuring the handle is valid."""
        if not glIsBuffer(self.handle):
            raise RuntimeError(f"Invalid buffer handle: {self.handle}")
        gl_bind_buffer(self.target, 0)

    def update(self, data: np.ndarray):
        self.data = data
        if data is not None:
            self.set_data(data)

    # ----------------------------
    # Data upload
    # ----------------------------
    def set_data(self, data: np.ndarray, usage: int = GLUsageHint.STATIC_DRAW) -> None:
        """
        Upload data to the GPU.

        :param data: NumPy array containing buffer data.
        :param usage: gl usage hint (e.g., GL_STATIC_DRAW, GL_DYNAMIC_DRAW).
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(f"Expected np.ndarray, got {type(data).__name__}")
        self.data = data
        self.dtype = self._map_dtype_to_gl(data.dtype.type)
        gl_buffer_data(
            target=self.target,
            size=data.nbytes,
            data=data,
            usage_hint=usage,
        )

    # ----------------------------
    # Vertex attribute state
    # ----------------------------
    def set_vertex_attributes(
        self,
        index: int,
        data: np.ndarray = None,
        size: int = None,
        normalized: bool = False,
        stride: int = 0,
        offset: int = 0,
        dtype: int = None,
        pointer: ctypes.c_void_p = None,
    ) -> None:
        """
        Set the vertex attribute pointer configuration.

        :param index: Attribute index in the VAO.
        :param data: Optional data array to store alongside attribute info.
        :param size: Number of components per vertex (1-4).
        :param normalized: Whether values should be normalized.
        :param stride: Byte offset between consecutive attributes.
        :param offset: Byte offset of the first attribute.
        :param dtype: gl data type (e.g., GL_FLOAT).
        :param pointer: Offset pointer for glVertexAttribPointer.
        """
        self.index = index
        if data is not None:
            self.data = data
        self.components = size or self.components
        self.normalized = normalized
        self.stride = stride
        self.offset = offset
        self.dtype = dtype or self.dtype
        self.pointer = pointer if pointer is not None else ctypes.c_void_p(0)

    def configure(self) -> None:
        """Enable and configure the vertex attribute array."""
        if self.index is None:
            raise ValueError("Vertex attribute index is not set.")
        gl_enable_vertex_array(self.index)
        normalized = GLBoolean.TRUE if self.normalized else GLBoolean.FALSE
        offset = self.pointer.value if self.pointer is not None else 0
        gl_vertex_attrib_pointer(
            index=self.index,
            size=self.components,
            num_type=self.dtype,
            normalized=normalized,
            stride=self.stride,
            offset=offset,
        )

    # ----------------------------
    # Helpers
    # ----------------------------
    @property
    def index_count(self) -> int:
        """Number of vertices/indices in this buffer."""
        return len(self.data) if self.data is not None else 0

    @classmethod
    def _map_dtype_to_gl(cls, dtype) -> int:
        """Map a NumPy dtype to the corresponding gl constant."""
        return cls._GL_TYPE_MAP.get(dtype, GLNumeric.FLOAT)

    # ----------------------------
    # Debug
    # ----------------------------
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        data_preview = repr(self.data)
        if len(data_preview) > 100:
            data_preview = data_preview[:97] + "..."
        return (
            f"{class_name}(index={self.index}, handle={self.handle}, pointer={self.pointer}, "
            f"target={self.target}, size={self.components}, stride={self.stride}, offset={self.offset}, "
            f"dtype={self.dtype}, normalized={self.normalized}, data={data_preview})"
        )

    def allocate(self, data: np.ndarray, usage: int = GLUsageHint.STATIC_DRAW):
        """Initial allocation (glBufferData)"""
        self.bind()
        self.buffer_size = data.nbytes
        gl_buffer_data(
            target=self.target,
            size=data.nbytes,
            data=data,
            usage_hint=usage,
        )

    def update_data(self, data: np.ndarray, offset: int = 0):
        """Upload buffer contents; prefer SubData, fall back to full Data if needed.

        Non-contiguous NumPy arrays can make ``glBufferSubData`` fail with
        ``GL_INVALID_VALUE`` (1281) under PyOpenGL; normalize layout first.
        If SubData still fails (e.g. stale ``buffer_size`` vs GPU store), reallocate.
        """
        if not data.flags.c_contiguous:
            data = np.ascontiguousarray(data)
        self.bind()

        if data.nbytes > self.buffer_size:
            # Fallback: reallocate only if absolutely required
            gl_buffer_data(
                target=self.target,
                size=data.nbytes,
                data=data,
                usage_hint=GLUsageHint.DYNAMIC_DRAW,
            )
            self.buffer_size = data.nbytes
        else:
            try:
                glBufferSubData(self.target, offset, data.nbytes, data)
            except _gl_err.GLError:
                gl_buffer_data(
                    target=self.target,
                    size=data.nbytes,
                    data=data,
                    usage_hint=GLUsageHint.DYNAMIC_DRAW,
                )
                self.buffer_size = data.nbytes
