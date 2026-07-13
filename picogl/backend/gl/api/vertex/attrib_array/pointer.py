"""
Defines and configures a vertex attribute pointer for a vertex array object (VAO).

This module provides functionality to specify layout organization for vertex attribute
data within a vertex buffer object (VBO). It enables the definition of how data flows
to the vertex shader. Primarily utilized in OpenGL rendering workflows for handling
vertex attributes.

Functions:
- gl_vertex_attrib_pointer: Configures a single vertex attribute pointer.
"""

from OpenGL.GL import glVertexAttribPointer

from picogl.backend.gl.enums import GLNumeric
from picogl.boolean import GLBoolean


def gl_vertex_attrib_pointer(
    index,
    size: int = 3,
    type: GLNumeric = GLNumeric.FLOAT,
    normalized: GLBoolean = GLBoolean.FALSE,
    stride: int = 0,
    pointer=None,
):
    """
    Configures a vertex attribute pointer for the currently bound vertex array object (VAO).

    This function specifies the organization of vertex attribute data in a vertex buffer
    object (VBO). It defines the layout of data that will be passed to the vertex shader.

    Parameters:
    index : int
        The index of the generic vertex attribute to be specified.
    size : int, optional
        The number of components per generic vertex attribute. Must be 1, 2, 3, or 4.
        Default is 3.
    type : GLNumeric, optional
        Data type of each component in the array. Default is GLNumeric.FLOAT.
    normalized : GLBoolean, optional
        Specifies whether fixed-point data values should be normalized or converted
        directly as fixed-point values when accessed. Default is GLBoolean.FALSE.
    stride : int, optional
        Byte offset between consecutive vertex attributes. Default is 0.
    pointer : object, optional
        Offset of the first component of the first generic vertex attribute in the array.
        Default is None.
    """
    glVertexAttribPointer(index, size, type, normalized, stride, pointer)
