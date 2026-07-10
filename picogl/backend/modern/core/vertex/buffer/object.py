"""Modern VBO"""

import numpy as np
from picogl.backend.gl.enums import GLBufferTarget
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.gl.api.glcleanup import gl_delete_buffers
from picogl.backend.modern.core.vertex.base import VertexBuffer


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

    def delete(self):
        if self.handle:
            gl_delete_buffers(1, [self.handle])
            self.handle = None
