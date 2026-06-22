"""
Legacy VBO
"""

import ctypes

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_5 import glBufferSubData
from picogl.backend.gl.enums import GLBufferTarget, GLNumeric, GLUsageHint
from picogl.backend.gl.wrappers import gl_buffer_data
from picogl.backend.gl.wrappers.generate_buffers import gl_generate_buffers
from picogl.backend.modern.core.vertex.base import VertexBuffer


class LegacyVBO(VertexBuffer):
    """Legacy OpenGL Vertex Buffer Object (VBO) or Element Buffer Object (EBO)."""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GLBufferTarget.ARRAY,
        configure: bool = True,
        size: int = 3,
        stride: int = 0,
        dtype: int = GLNumeric.FLOAT,
        pointer: ctypes.c_void_p = ctypes.c_void_p(0),
    ):
        self.nbytes = None
        self.components = size
        if handle is None:
            handle = gl_generate_buffers(1)

        super().__init__(
            handle=handle,
            data=data,
            target=target,
            size=size,
            stride=stride,
            dtype=dtype,
            pointer=pointer,
        )

        if data is not None:
            self.set_data(data)

        self.bind()
        try:
            if configure and type(self) is not LegacyVBO:
                self.configure()
        finally:
            self.unbind()

    def __enter__(self):
        self.bind()
        self.configure()  # Ensure subclasses override this method appropriately
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unbind()

    def set_data(self, data: np.ndarray, usage: int = GLUsageHint.STATIC_DRAW) -> None:
        """
        Upload data to the GPU.

        :param data: NumPy array containing the data to upload.
        :param usage: OpenGL usage hint (e.g., GL_STATIC_DRAW).
        :raises ValueError: If the data is not a NumPy array.
        """
        if data is None or not isinstance(data, np.ndarray):
            raise ValueError("Data must be a non-null NumPy array.")

        self.data = data
        self.dtype = self._map_dtype_to_gl(data.dtype.type)
        self.bind()
        try:
            gl_buffer_data(
                target=self.target,
                size=data.nbytes,
                data=data,
                usage_hint=usage,
            )
            self.nbytes = data.nbytes
        finally:
            self.unbind()

    def allocate(self, data: np.ndarray, usage: int = GLUsageHint.STATIC_DRAW):
        """Initial allocation (glBufferData)"""
        self.bind()
        self.nbytes = data.nbytes
        gl_buffer_data(
            target=self.target,
            size=data.nbytes,
            data=data,
            usage_hint=usage,
        )

    def update_data(self, data: np.ndarray, offset: int = 0):
        self.bind()

        # First-time allocation case
        if self.nbytes is None:
            gl_buffer_data(
                target=self.target,
                size=data.nbytes,
                data=data,
                usage_hint=GLUsageHint.DYNAMIC_DRAW,
            )
            self.nbytes = data.nbytes
            return

        if data.nbytes > self.nbytes:
            gl_buffer_data(
                target=self.target,
                size=data.nbytes,
                data=data,
                usage_hint=GLUsageHint.DYNAMIC_DRAW,
            )
            self.nbytes = data.nbytes
        else:
            glBufferSubData(self.target, offset, data.nbytes, data)

    def configure(self):
        """Configure the buffer (default implementation does nothing)."""
        pass
