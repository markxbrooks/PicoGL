import numpy as np

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.numerical import GLNumeric
from picogl.wrappers.pointer import gl_color_array_pointer


class LegacyColorVBO(LegacyVBO):
    """Specialized VBO class for colour attributes."""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        dtype: int = GLNumeric.FLOAT,
    ):
        """
        Initialize a colour VBO.

        :param handle: Existing OpenGL buffer handle (optional).
        :param data: Numpy array with colour data (optional).
        :param size: Number of components per colour (3=RGB, 4=RGBA).
        """
        super().__init__(handle=handle, size=size, dtype=dtype)
        if data is not None:
            self.set_data(data)

    def configure(self):
        """Configure vertex attribute pointer for colors."""
        # assert self.components in (3, 4), f"Invalid color component count: {self.components}"
        gl_color_array_pointer(
            pointer=self.pointer,
            size=self.components,
            num_type=self.dtype,
            stride=self.stride,
        )
