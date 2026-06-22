from contextlib import contextmanager

from OpenGL.GL import glBegin, glEnd
from picogl.backend.gl.enums import GLDrawMode

_immediate_active = False


@contextmanager
def immediate_drawing(draw_mode: GLDrawMode = GLDrawMode.LINE_STRIP):
    global _immediate_active

    if _immediate_active:
        raise RuntimeError("Nested glBegin/glEnd is not allowed")

    assert isinstance(draw_mode, GLDrawMode)

    try:
        _immediate_active = True
        glBegin(draw_mode.value)
        yield
    finally:
        glEnd()
        _immediate_active = False
