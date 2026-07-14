from typing import Optional

from OpenGL.GL import glDeleteVertexArrays

from picogl.backend.gl.api import gl_bind_buffer
from picogl.backend.gl.api.enable_vertex_array import gl_enable_vertex_array
from picogl.backend.gl.api.glcleanup import gl_delete_buffers
from picogl.backend.gl.api.vertex.attrib_pointer import \
    gl_vertex_attrib_pointer
from picogl.backend.gl.api.vertex.generate_array import \
    gl_generate_vertex_array
from picogl.backend.gl.api.vertex.vertex_array import gl_bind_vertex_array
from picogl.backend.gl.enums import GLBufferTarget
from picogl.gpu.buffers.attributes import LayoutDescriptor
from picogl.gpu.buffers.base import VertexBase


class ModernVertexArrayGroup(VertexBase):
    """
    ModernVertexArrayGroup

    Modern backend (uses a real VAO)
    """

    def init(self):
        self.vao = gl_generate_vertex_array(1)
        self.nbo = None
        self.cbo = None
        self.vbo = None
        self.ebo = None
        self.layout: Optional[LayoutDescriptor] = None
        self._configured = False

    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        self.nbo = nbo
        self.cbo = cbo
        self.vbo = vbo
        self.ebo = ebo

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """
        set_layout

        :param layout: LayoutDescriptor: The layout descriptor to define the vertex attribute format.
        :raises: None

        Sets the layout for the rendering setup by binding the buffers and configuring the attributes.
        The state is stored in the Vertex Array Object (VAO). This method assumes a single Vertex Buffer
        Object (VBO) holds all position data but can be adapted as required. Handles optional usage of
        Normal Buffer Object (NBO) and Element Buffer Object (EBO) if present.
        """
        self.layout = layout
        gl_bind_vertex_array(self.vao.handle)

        if self.vbo is not None:
            gl_bind_buffer(
                GLBufferTarget.ARRAY, getattr(self.vbo.handle, "_id", self.vbo.handle)
            )
        if self.nbo is not None:
            # If you have multiple buffers, bind as needed per attribute
            pass  # adapt as needed

        if self.layout:
            for attr in self.layout.attributes:
                gl_enable_vertex_array(attr.index)
                gl_vertex_attrib_pointer(
                    index=attr.index,
                    size=attr.size,
                    num_type=attr.type,
                    normalized=attr.normalized,
                    stride=attr.stride,
                    offset=attr.offset,
                )
        if self.ebo is not None:
            gl_bind_buffer(
                GLBufferTarget.ELEMENT, getattr(self.ebo.handle, "_id", self.ebo)
            )

        gl_bind_vertex_array(0)
        self._configured = True

    def bind(self) -> None:
        gl_bind_vertex_array(self.vao)

    def unbind(self) -> None:
        gl_bind_vertex_array(0)

    def delete(self) -> None:
        if self.vao:
            glDeleteVertexArrays([self.vao])
            self.vao = 0
        gl_delete_buffers(self.nbo)
        gl_delete_buffers(self.cbo)
        gl_delete_buffers(self.vbo)
        gl_delete_buffers(self.ebo)
        self.nbo = self.cbo = self.vbo = self.ebo = None
        self.layout = None
        self._configured = False
