"""
Draw a VAO with attributes
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS

from picogl.buffers.vao.configure import vao_configure_attributes
from picogl.wrappers.draw import gl_draw_arrays


def vao_draw_with_attributes(attributes: list, atom_count: int, mode: int = GL_POINTS):
    """
    vao_draw_with_attributes

    :param attributes: list Attributes for drawing.
    :param atom_count: int Number of vertices to draw.
    :param mode: int Enum specifying the gl_mode of drawing (default is GL_POINTS).

    Draw the VAO with the specified gl_mode and atom count.
    """
    vao_configure_attributes(attributes)
    gl_draw_arrays(atom_count, mode, first=0)
