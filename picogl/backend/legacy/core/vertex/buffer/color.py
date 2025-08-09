import numpy as np
from OpenGL.GL import glColorPointer

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyColorVBO(LegacyVBO):
    """Specialized Class for Color Buffers"""

    def __init__(self, handle: int = None, data: np.ndarray = None, size: int = 3):
        """constructor"""
        super().__init__(handle=handle, size=size)
        self.data = data
        if data is not None:
            self.set_data(data)
        self.bind()

    def configure(self):
        """Configure attributes specific to color atoms_buffers"""
        glColorPointer(self.size, self.dtype, self.stride, self.pointer)
