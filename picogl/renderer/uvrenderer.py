"""
Module providing the UvRenderer class for rendering 2D UV meshes using OpenGL.

The module implements a specific renderer for meshes defined with UV
coordinates and indices. The UvRenderer class is designed for lightweight UV
rendering tasks and operates using OpenGL buffers. It provides methods for
binding buffers and rendering the defined UV mesh content.
"""

from typing import Optional

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POLYGON_MODE

from picogl.backend.gl.api import (gl_bind_buffer, gl_disable_vertex_array,
                                   gl_draw_elements, gl_get_integerv)
from picogl.backend.gl.api.enable_vertex_array import gl_enable_vertex_array
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.enums import GLBufferTarget, GLDrawMode, GLNumeric
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.boolean import GLBoolean
from picogl.renderer import RendererBase
from picogl.renderer.initializable import Initializable


class UvRenderer(Initializable, RendererBase):
    """
    2D UV Renderer that draws a mesh using UV coordinates and indices.
    Follows the RendererBase interface.
    """

    def __init__(
        self,
        parent: object = None,
        vertex_shader_file: str = "glsl/utils/uv2d/vertex.glsl",
        fragment_shader_file: str = "glsl/utils/uv2d/fragment.glsl",
    ):
        super().__init__(parent)
        self.uv_buffer: Optional[int] = None
        self.indices_buffer: Optional[int] = None
        self.index_count: int = 0
        self.shader: ShaderProgram = ShaderProgram(
            vertex_source_file=vertex_shader_file,
            fragment_source_file=fragment_shader_file,
        )

    def bind(self, uv_buffer: int, indices_buffer: int, index_count: int) -> None:
        """
        Bind the UV and index buffers to the renderer.

        :param uv_buffer: OpenGL buffer ID containing UVs
        :param indices_buffer: OpenGL buffer ID containing indices
        :param index_count: Number of indices to draw
        """
        if not all(
            isinstance(x, int) for x in (uv_buffer, indices_buffer, index_count)
        ):
            raise ValueError(
                "uv_buffer, indices_buffer, and index_count must be integers"
            )
        self.ensure_initialized()
        self._setup(index_count, indices_buffer, uv_buffer)

    def _setup(self, index_count: int, indices_buffer: int, uv_buffer: int):
        self.uv_buffer = uv_buffer
        self.indices_buffer = indices_buffer
        self.index_count = index_count

    def _draw_model(self) -> None:
        """
        Draw the UV mesh. Called by RendererBase.render().
        """
        if (
            self.uv_buffer is None
            or self.indices_buffer is None
            or self.index_count == 0
        ):
            # Nothing to draw
            return

        # Save previous polygon mode
        prev_mode = gl_get_integerv(GL_POLYGON_MODE)
        prev_front_mode, prev_back_mode = prev_mode[0], prev_mode[1]

        with self.shader:
            # Assume shader attribute location 0 for UVs
            uv_loc = 0  # Alternatively, query dynamically with glGetAttribLocation
            gl_enable_vertex_array(uv_loc)
            gl_bind_buffer(GLBufferTarget.ARRAY, self.uv_buffer)
            gl_vertex_attrib_pointer(
                index=uv_loc,
                size=2,
                num_type=GLNumeric.FLOAT,
                normalized=GLBoolean.FALSE,
                stride=0,
                offset=None,
            )

            gl_bind_buffer(GLBufferTarget.ELEMENT, self.indices_buffer)

            # Wireframe rendering
            gl_polygon_mode(GLMaterialFace.FRONT, GLFillMode.LINE)
            gl_polygon_mode(GLMaterialFace.BACK, GLFillMode.LINE)

            gl_draw_elements(
                self.index_count,
                GLNumeric.UNSIGNED_SHORT,
                GLDrawMode.TRIANGLES,
                pointer=None,
            )

            gl_disable_vertex_array(uv_loc)

        # Restore previous polygon mode
        gl_polygon_mode(GLMaterialFace.FRONT, prev_front_mode)
        gl_polygon_mode(GLMaterialFace.BACK, prev_back_mode)
