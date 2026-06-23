"""
Legacy Position VBO

"""

import ctypes

import numpy as np

from picogl.backend.gl.enums import GLBufferTarget, GLNumeric
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.wrappers import gl_enable_legacy_client_state
from picogl.backend.gl.wrappers.pointer import gl_vertex_array_pointer
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO


class LegacyPositionVBO(LegacyVBO):
    """
    OpenGL buffer class specialized for storing and managing position data,
    commonly used for rendering ribbons_legacy-like meshdata.

    Inherits from LegacyVBO and adds behavior specific to position data,
    such as setting up the vertex pointer and handling data uploads.
    """

    SUPPORTED_GL_TYPES = GLNumeric.supported_gl_types()

    def __init__(
        self,
        handle: int = None,
        data: np.ndarray = None,
        size: int = 3,
        target: int = GLBufferTarget.ARRAY,
        dtype: int = GLNumeric.FLOAT,
    ):
        """Initialize the position VBO."""
        super().__init__(
            handle=handle, size=size, data=data, target=target, dtype=dtype
        )
        self.size = size
        self.data = data
        if data is not None:
            self.set_data(data)

    def configure(self):
        """Configure the vertex pointer for the position buffer.

        ``LegacyVBO.__enter__`` has already bound this buffer; do not unbind here
        or the vertex array may lose its buffer object binding before ``glDraw*``.
        """
        if self.dtype not in self.SUPPORTED_GL_TYPES:
            raise ValueError(f"Unsupported GL data type: {self.dtype}")
        gl_enable_legacy_client_state(GLClientState.VERTEX)
        gl_vertex_array_pointer(
            pointer=ctypes.c_void_p(0),
            size=self.components,
            num_type=self.dtype,
            stride=self.stride,
        )
