"""
draw elements
"""

from picogl.backend.gl.enums import GLDrawMode, GLNumeric
from picogl.backend.gl.wrappers import gl_draw_elements
from picogl.backend.gl.wrappers.vertex_array import gl_bind_vertex_array
from picogl/backend/modern/core/elements/vertex-array import bound_vertex_array

    
def draw_elements(
    vao: int,
    index_count: int,
    mode: int = GLDrawMode.TRIANGLES,  # or int
    index_type: int = GLIndexType.UNSIGNED_INT,  # or GLNumeric.UNSIGNED_INT
    pointer: Optional[Any] = None
) -> None:
    """
    Bind a VAO and issue glDrawElements for the bound element buffer.

    - vao: Vertex Array Object to bind
    - index_count: Number of indices to draw
    - mode: GL draw mode (e.g., GL_LINES, GL_TRIANGLES)
    - index_type: Type of indices (e.g., GL_UNSIGNED_INT)
    - pointer: Optional client-side index data; if None, the bound EBO is used
    """
    with bound_vertex_array(vao):
        gl_draw_elements(index_count=index_count, index_type=index_type, mode=mode, pointer=pointer, offset=0)
