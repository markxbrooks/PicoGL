from typing import Dict, Type

from OpenGL import GL
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_VERTEX_ARRAY, GL_COLOR_ARRAY, glDrawArrays,
    glEnableClientState, glDisableClientState, glVertexPointer, glColorPointer
)
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FLOAT

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.color import LegacyColorVBO
from picogl.backend.legacy.core.vertex.buffer.position import LegacyPositionVBO
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.vertex.legacy import VertexBufferGroup
from picogl.logger import Logger as log


class AxesVBG(VertexBufferGroup):
    def __init__(self):
        super().__init__()
        self.vbo_classes: Dict[str, Type[LegacyVBO]] = {
            "vbo": LegacyPositionVBO,
            "cbo": LegacyColorVBO,
        }

    @property
    def index_count(self) -> int:
        """Return the number of vertices for drawing."""
        # For axes, we have 6 vertices (2 per axis line)
        # Override the base class property which tries to get count from EBO
        return 6

    def draw(self, index_count: int = None, mode: int = GL.GL_LINES):
        """Draw the axes using custom implementation for legacy OpenGL."""
        if not index_count:
            index_count = self.index_count
            
        try:
            # Use legacy client states for compatibility
            with legacy_client_states(GL_VERTEX_ARRAY, GL_COLOR_ARRAY):
                # Bind and configure each VBO manually for legacy OpenGL
                if 'vbo' in self.named_vbos:
                    vbo = self.named_vbos['vbo']
                    vbo.bind()
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glVertexPointer(3, GL_FLOAT, 0, None)
                    
                if 'cbo' in self.named_vbos:
                    cbo = self.named_vbos['cbo']
                    cbo.bind()
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointer(3, GL_FLOAT, 0, None)
                    
                # Draw the arrays
                glDrawArrays(mode, 0, index_count)
                
                # Clean up
                if 'cbo' in self.named_vbos:
                    glDisableClientState(GL_COLOR_ARRAY)
                if 'vbo' in self.named_vbos:
                    glDisableClientState(GL_VERTEX_ARRAY)
                    
        except Exception as e:
            log.error(f"Error in AxesVBG.draw(): {e}")
            raise