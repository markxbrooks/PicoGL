import ctypes

import numpy as np
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.core.enums.buffer_target import GLBufferTarget
from picogl.core.enums.draw_mode import GLDrawMode
from picogl.core.enums.index_type import GLIndexType
from picogl.core.enums.numerical import GLNumeric


class LegacyEBO(LegacyVBO):
    """Legacy Element Buffer Object (EBO)"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        target: int = GLBufferTarget.ELEMENT,
        size: int = 3,
        dtype: int = GLNumeric.FLOAT,
    ):
        """constructor"""
        super().__init__(
            handle=handle, data=data, target=target, size=size, dtype=dtype
        )

    def configure(self):
        """
        configure

        :return: None
        Element Buffers don't use vertex attributes—nothing to configure."""
        pass
