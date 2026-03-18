import ctypes
from typing import Optional

# from buffers.glcleanup import delete_buffer
from OpenGL.GL import (glDeleteVertexArrays, glGenVertexArrays,
                       glVertexAttribPointer)
from OpenGL.raw.GL.VERSION.GL_1_5 import (GL_ARRAY_BUFFER,
                                          GL_ELEMENT_ARRAY_BUFFER,
                                          glBindBuffer)
from OpenGL.raw.GL.VERSION.GL_2_0 import glEnableVertexAttribArray
from OpenGL.raw.GL.VERSION.GL_3_0 import glBindVertexArray
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer


class ModernVertexArrayGroup(VertexBase):
    """
    ModernVertexArrayGroup

    Modern backend (uses a real VAO)
    """

    def init(self):
        self.vao = glGenVertexArrays(1)
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
        glBindVertexArray(self.vao.handle)

        if self.vbo is not None:
            glBindBuffer(
                GL_ARRAY_BUFFER, getattr(self.vbo.handle, "_id", self.vbo.handle)
            )
        if self.nbo is not None:
            # If you have multiple buffers, bind as needed per attribute
            pass  # adapt as needed

        if self.layout:
            for attr in self.layout.attributes:
                glEnableVertexAttribArray(attr.index)
                glVertexAttribPointer(
                    attr.index,
                    attr.size,
                    attr.type,
                    attr.normalized,
                    attr.stride,
                    ctypes.c_void_p(attr.offset),
                )
        if self.ebo is not None:
            glBindBuffer(
                GL_ELEMENT_ARRAY_BUFFER, getattr(self.ebo.handle, "_id", self.ebo)
            )

        glBindVertexArray(0)
        self._configured = True

    def bind(self) -> None:
        glBindVertexArray(self.vao)

    def unbind(self) -> None:
        glBindVertexArray(0)

    def delete(self) -> None:
        if self.vao:
            glDeleteVertexArrays([self.vao])
            self.vao = 0
        delete_buffer(self.nbo)
        delete_buffer(self.cbo)
        delete_buffer(self.vbo)
        delete_buffer(self.ebo)
        self.nbo = self.cbo = self.vbo = self.ebo = None
        self.layout = None
        self._configured = False
