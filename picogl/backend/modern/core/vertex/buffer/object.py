"""Modern VBO"""

import numpy as np
from OpenGL.GL import glGenBuffers

from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.state.draw_mode import GLBufferTarget


class ModernVBO(VertexBuffer):
    """Vertex Buffer Object"""

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GLBufferTarget.ARRAY,
        index: int = None,
    ):
        """ """
        if handle is None:
            handle = glGenBuffers(1)
        super().__init__(
            handle=handle, size=size, data=data, target=target, index=index
        )
