"""Legacy raster position wrappers."""

from OpenGL.raw.GL.VERSION.GL_1_0 import glRasterPos3f


def gl_raster_pos_3f(x: float, y: float, z: float) -> None:
    """Set the current raster position."""
    glRasterPos3f(x, y, z)
