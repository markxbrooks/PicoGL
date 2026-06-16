import numpy as np
from OpenGL.GL import glNormalPointer

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.state.draw_mode import GLDataType


class LegacyNormalVBO(LegacyVBO):
    """Specialized Class for Position Buffers"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        dtype: int = GLDataType.FLOAT,
    ):
        """constructor"""
        super().__init__(handle=handle, size=size, dtype=dtype)
        self.data = data
        if data is not None:
            self.set_data(data)
        self.bind()

    def configure(self):
        """Configure attributes specific to position atoms_buffers"""
        glNormalPointer(self.dtype, 0, None)
