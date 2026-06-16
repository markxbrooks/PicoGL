"""
draw legacy bond vao
"""

from contextlib import contextmanager

from decologr import Decologr as log
from OpenGL.GL import glDrawArrays

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.vertex.legacy import VertexBufferGroup
from picogl.numerical import GLNumeric
from picogl.state.client import GLClientState
from picogl.state.draw_mode import GLDrawMode


def gl_draw_arrays(index_count: int, mode: int):
    """gl draw arrays"""
    glDrawArrays(mode, 0, index_count)


@contextmanager
def draw_arrays(mode: GLDrawMode, first: int, count: int):
    """
    draw_arrays

    :param mode: GLDrawMode
    :param first: int
    :param count: int
    :return: None
    """
    try:
        yield lambda: gl_draw_arrays(mode, count)
    finally:
        pass


@contextmanager
def bound_legacy_buffers(vbo: LegacyVBO, cbo: LegacyVBO, nbo: LegacyVBO):
    with legacy_client_states(
        GLClientState.VERTEX, GLClientState.COLOR, GLClientState.NORMAL
    ):
        with vbo, cbo, nbo:
            yield
