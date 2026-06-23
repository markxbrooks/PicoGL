import numpy as np

from picogl.backend.gl.enums import GLNumeric
from picogl.backend.gl.wrappers.pointer import gl_normal_array_pointer
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyNormalVBO(LegacyVBO):
    """Specialized Class for Position Buffers"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        dtype: int = GLNumeric.FLOAT,
    ):
        """constructor"""
        super().__init__(handle=handle, size=size, dtype=dtype)
        self.data = data
        if data is not None:
            self.set_data(data)
        self.bind()

    def configure(self):
        """Configure attributes specific to position atoms_buffers"""
        gl_normal_array_pointer(pointer=None, num_type=self.dtype, stride=0)
