"""
Element Buffer Object (EBO) Management for Modern OpenGL Rendering.

This module defines the `ElementBufferObject` class, which encapsulates the
OpenGL element data buffer (also known as an index buffer). It is used to
store indices that OpenGL uses to decide which vertices to draw, allowing
for efficient reuse of vertex data in complex models.

The class handles:
- Creation and deletion of the EBO on the GPU.
- Binding and unbinding of the buffer.
- Storage of element/index data along with configuration parameters.
- Uploading the data to the GPU with :func:`picogl.wrappers.data.gl_buffer_data`.

Example usage:

.. code-block:: python

    import numpy as np

    from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
    from picogl.backend.gl.state.draw_mode import GLUsageHint

    indices = np.array([0, 1, 2], dtype=np.uint32)
    ebo = ModernEBO(data=indices)
    with ebo:
        ebo.set_element_attributes(
            data=indices,
            size=indices.nbytes,
            dtype=GLUsageHint.STATIC_DRAW,
        )
        ebo.configure()
"""

from typing import Optional

import numpy as np
from picogl.backend.gl.enums import GLBufferTarget, GLUsageHint
from picogl.backend.gl.api import gl_buffer_data
from picogl.backend.gl.api.buffer.generate import gl_generate_buffers
from picogl.backend.modern.core.vertex.base import VertexBuffer


class ModernEBO(VertexBuffer):
    """
    OpenGL element data buffer (also known as an index buffer)
    """

    def __init__(
        self,
        handle: Optional[int] = None,
        data: Optional[np.ndarray] = None,
        size: int = 3,
        target: int = GLBufferTarget.ELEMENT,
    ):
        """ """
        if handle is None:
            handle = gl_generate_buffers(1)
        super().__init__(handle=handle, size=size, data=data, target=target)
        if data is not None:
            self.size = data.nbytes

    def set_element_attributes(
        self, data: np.ndarray, size: int, dtype: int = GLUsageHint.STATIC_DRAW
    ):
        """
        set_element_attributes

        :param data: np.ndarray
        :param size: int
        :param dtype: int
        :return: None
        """
        self.data = data
        self.size = size
        self.dtype = dtype

    def configure(self):
        """
        configure

        :return: None
        """
        if self.data is None:
            raise ValueError("ModernEBO has no element data to upload")
        byte_size = getattr(self, "size", None) or self.data.nbytes
        gl_buffer_data(
            target=GLBufferTarget.ELEMENT,
            size=byte_size,
            data=self.data,
            usage_hint=self.dtype,
        )
