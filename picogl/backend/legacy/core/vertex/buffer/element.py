import ctypes

import numpy as np
from OpenGL.GL import glDrawElements

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.state.draw_mode import GLBufferTarget, GLDataType, GLDrawMode, GLIndexType


class LegacyEBO(LegacyVBO):
    """Legacy Element Buffer Object (EBO)"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GLBufferTarget.ELEMENT_ARRAY_BUFFER,
        size: int = 3,
        dtype: int = GLDataType.FLOAT,
    ):
        """constructor"""
        super().__init__(
            handle=handle, data=data, target=target, size=size, dtype=dtype
        )

    def draw(
        self,
        index_count: int,
        index_type: int = GLIndexType.UNSIGNED_INT,
        mode: int = GLDrawMode.LINES,
    ):
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
