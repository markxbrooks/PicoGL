import ctypes

import numpy as np
from OpenGL.GL import GL_FLOAT, glDrawElements
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ELEMENT_ARRAY_BUFFER
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyEBO(LegacyVBO):
    """Legacy Element Buffer Object (EBO)"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GL_ELEMENT_ARRAY_BUFFER,
        size: int = 3,
        dtype: int = GL_FLOAT
    ):
        """constructor"""
        super().__init__(handle=handle, data=data, target=target, size=size, dtype=dtype)

    def draw(self, index_count: int, index_type: int = GL_UNSIGNED_INT, mode: int = GL_LINES):
        if index_count <= 0:
            return

        # MUST already be bound externally
        glDrawElements(mode, index_count, index_type, None)

    def configure(self):
        """
        configure

        :return: None
        Element Buffers don't use vertex attributes—nothing to configure."""
        pass
