"""
draw legacy bond vao
"""

from contextlib import contextmanager

from decologr import Decologr as log
from picogl.backend.legacy.core.vertex.buffer.client_states import \
    legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.core.enums.draw_mode import GLDrawMode
from picogl.gpu.buffers.vertex.legacy import VertexBufferGroup
from picogl.state.client import GLClientState
from picogl.wrappers.draw import gl_draw_arrays


def gl_draw_arrays_legacy(index_count: int, mode: int):
    """Legacy bond/atom VBG draw helper."""
    gl_draw_arrays(index_count, mode, first=0)


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
        yield lambda: gl_draw_arrays_legacy(mode, count)
    finally:
        pass


@contextmanager
def bound_legacy_buffers(vbo: LegacyVBO, cbo: LegacyVBO, nbo: LegacyVBO):
    with legacy_client_states(
        GLClientState.VERTEX, GLClientState.COLOR, GLClientState.NORMAL
    ):
        with vbo, cbo, nbo:
            yield
