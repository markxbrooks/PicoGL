import numpy as np
from OpenGL.GL import glDrawElements, glVertexPointer
from OpenGL.raw.GL._types import GL_BYTE, GL_FLOAT, GL_INT, GL_SHORT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_DOUBLE,
    GL_VERTEX_ARRAY,
    glDrawArrays,
    glEnableClientState,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyPositionVBO(LegacyVBO):
    """
    OpenGL buffer class specialized for storing and managing position data,
    commonly used for rendering ribbons_legacy-like geometry.

    Inherits from LegacyVBO and adds behavior specific to position data,
    such as setting up the vertex pointer and handling data uploads.
    """

    SUPPORTED_GL_TYPES = {GL_FLOAT, GL_DOUBLE, GL_INT, GL_SHORT, GL_BYTE}

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GL_ARRAY_BUFFER,
    ):
        """Initialize the position VBO."""
        super().__init__(handle=handle, size=size, data=data, target=target)
        self.size = size
        self.data = data
        if data is not None:
            self.set_data(data)

    def draw_arrays(self, count: int = None, mode: int = GL_TRIANGLES):
        if count is None:
            count = len(self.data) // self.size
        with legacy_client_states(GL_VERTEX_ARRAY):
            glDrawArrays(mode, 0, count)

    def draw(
        self,
        index_count: int = None,
        index_type: int = GL_UNSIGNED_INT,
        mode: int = GL_TRIANGLES,
    ):
        """
        Draw the buffer.

        :param index_count: Number of indices to draw (default: self.index_count).
        :param index_type: Data type of indices (e.g., GL_UNSIGNED_INT).
        :param mode: OpenGL drawing mode (e.g., GL_TRIANGLES).
        """
        if index_count is None:
            index_count = self.index_count
        with legacy_client_states(GL_VERTEX_ARRAY):
            glDrawElements(mode, index_count, index_type, self.pointer)

    def configure(self):
        """Configure the vertex pointer for the position buffer."""
        self.bind()
        try:
            if self.dtype not in self.SUPPORTED_GL_TYPES:
                raise ValueError(f"Unsupported GL data type: {self.dtype}")
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(self.size, self.dtype, self.stride, self.pointer)
        finally:
            self.unbind()
