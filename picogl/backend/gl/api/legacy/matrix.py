from contextlib import contextmanager
from OpenGL.GL import glPushMatrix, glPopMatrix

@contextmanager
def gl_pushed_matrix():
    """Push and automatically restore the current matrix."""
    glPushMatrix()
    try:
        yield
    finally:
        glPopMatrix()