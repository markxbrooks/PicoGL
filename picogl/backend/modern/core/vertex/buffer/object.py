"""Modern VBO"""

import numpy as np

from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.state.draw_mode import GLBufferTarget
from picogl.wrappers.generate_buffers import gl_generate_buffers


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
            handle = gl_generate_buffers(1)
        super().__init__(
            handle=handle, size=size, data=data, target=target, index=index
        )
