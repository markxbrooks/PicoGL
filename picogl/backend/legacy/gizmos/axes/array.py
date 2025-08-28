from typing import Dict, Type

from OpenGL import GL
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_VERTEX_ARRAY, GL_COLOR_ARRAY, glDrawArrays

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.color import LegacyColorVBO
from picogl.backend.legacy.core.vertex.buffer.position import LegacyPositionVBO
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.vertex.legacy import VertexBufferGroup


class AxesVBG(VertexBufferGroup):
    def __init__(self):
        super().__init__()
        self.vbo_classes: Dict[str, Type[LegacyVBO]] = {
            "vbo": LegacyPositionVBO,
            "cbo": LegacyColorVBO,
        }

    def draw(self, index_count: int = None, mode: int = GL.GL_LINES):
        if not index_count:
            index_count = self.index_count
        with legacy_client_states(GL_VERTEX_ARRAY, GL_COLOR_ARRAY):
            with self.vbo, self.cbo:
                glDrawArrays(mode, 0, index_count)