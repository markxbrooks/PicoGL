"""
Legacy VBO
"""

import ctypes

import numpy as np
from OpenGL.GL import glBufferData, glGenBuffers
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FLOAT, GL_UNSIGNED_INT, GL_LINES
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER, GL_STATIC_DRAW

from picogl.backend.modern.core.vertex.base import VertexBuffer


class LegacyVBO(VertexBuffer):
    """Legacy OpenGL Vertex Buffer Object (VBO) or Element Buffer Object (EBO)."""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GL_ARRAY_BUFFER,
        configure: bool = True,
        size: int = 3,
        stride: int = 0,
        dtype: int = GL_FLOAT,
        pointer: ctypes.c_void_p = ctypes.c_void_p(0),
    ):
        if handle is None:
            handle = glGenBuffers(1)

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

    def set_data(self, data: np.ndarray, usage: int = GL_STATIC_DRAW) -> None:
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
            glBufferData(self.target, data.nbytes, data, usage)
        finally:
            self.unbind()

    def configure(self):
        """Configure the buffer (default implementation does nothing)."""
        pass

    def draw(
        self, index_count: int, index_type: int = GL_UNSIGNED_INT, mode: int = GL_LINES
    ):
        """Draw call (must be implemented in subclasses)."""
        raise NotImplementedError("Subclasses must implement draw()!")
