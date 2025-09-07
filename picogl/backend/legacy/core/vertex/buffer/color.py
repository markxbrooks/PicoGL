import numpy as np
from OpenGL.GL import glColorPointer, GL_FLOAT

from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyColorVBO(LegacyVBO):
    """Specialized VBO class for color attributes."""

    def __init__(self, handle: int = None, data: np.ndarray = None, size: int = 3, dtype: int = GL_FLOAT):
        """
        Initialize a color VBO.

        :param handle: Existing OpenGL buffer handle (optional).
        :param data: Numpy array with color data (optional).
        :param size: Number of components per color (3=RGB, 4=RGBA).
        """
        super().__init__(handle=handle, size=size, dtype=dtype)
        if data is not None:
            self.set_data(data)
        # Binding in __init__ is optional – keep if consistent with other subclasses
        self.bind()

    def configure(self):
        """Configure vertex attribute pointer for colors."""
        glColorPointer(self.size, self.dtype, self.stride, self.pointer)
