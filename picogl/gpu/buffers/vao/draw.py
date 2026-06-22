"""
Draw a VAO with attributes
"""

from picogl.core.enums.draw_mode import GLDrawMode
from picogl.gpu.buffers.vao.configure import vao_configure_attributes
from picogl.wrappers.draw import gl_draw_arrays


def vao_draw_with_attributes(
    attributes: list, atom_count: int, mode: int = GLDrawMode.POINTS
):
    """
    vao_draw_with_attributes

    :param attributes: list Attributes for drawing.
    :param atom_count: int Number of vertices to draw.
    :param mode: int Enum specifying the gl_mode of drawing (default is GL_POINTS).

    Draw the VAO with the specified gl_mode and atom count.
    """
    vao_configure_attributes(attributes=attributes)
    gl_draw_arrays(index_count=atom_count, mode=mode, first=0)
