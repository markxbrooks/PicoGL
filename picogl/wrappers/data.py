"""
gl buffer data wrapper

"""
from OpenGL.GL import glBufferData

from picogl.state.draw_mode import GLBufferTarget, GLUsageHint


def gl_buffer_data(target: GLBufferTarget = GLBufferTarget.ARRAY,
                   size: int = 0,
                   data = None,
                   usage_hint: GLUsageHint = GLUsageHint.STATIC_DRAW):
    """gl bind buffer"""
    assert data is not None
    assert size > 0
    glBufferData(target, size, data, usage_hint)