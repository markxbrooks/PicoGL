"""
VertexArrayGroup

Legacy backend (no real GL VAO support)
"""

import ctypes
from typing import Optional, Any

import numpy as np
from OpenGL.GL import glVertexAttribPointer
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS, GL_TRIANGLES, GL_UNSIGNED_INT, GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
    glDrawArrays,
    glDrawElements,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import (
    GL_ARRAY_BUFFER,
    GL_ELEMENT_ARRAY_BUFFER,
    glBindBuffer,
)
from OpenGL.raw.GL.VERSION.GL_2_0 import (
    glDisableVertexAttribArray,
    glEnableVertexAttribArray,
)

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.color import LegacyColorVBO
from picogl.backend.legacy.core.vertex.buffer.element import LegacyEBO
from picogl.backend.legacy.core.vertex.buffer.normal import LegacyNormalVBO
from picogl.backend.legacy.core.vertex.buffer.position import LegacyPositionVBO
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer_object
from picogl.buffers.vertex.aliases import NAME_ALIASES
from picogl.logger import Logger as log


class VertexBufferGroup(VertexBase):
    """Container for legacy VBOs, mimicking VAO interface."""

    def __init__(self):
        super().__init__()
        # self.index_count = 0
        self.handle = 0  # Does absolutely nothing
        self.vao = (
            None  # Bonds Vertex Array Object. Does absolutely nothing, but is needed
        )
        self.vbo = None  # Atom Vertex Buffer Object
        self.cbo = None  # Color Vertex Buffer Object
        self.nbo = None  # Normal Vertex Buffer Object
        self.ebo = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None
        self.named_vbos: dict[str, LegacyVBO] = {}  # store by semantic name
        self.vbo_classes = {
            "vbo": LegacyPositionVBO,
            "cbo": LegacyColorVBO,
            "ebo": LegacyEBO,
            "nbo": LegacyNormalVBO,
        }

    def add_vbo_object(self, name: str, vbo: "LegacyVBO") -> "LegacyVBO":
        """Register a VBO by semantic name or shorthand alias."""
        # normalize to canonical key
        canonical = NAME_ALIASES.get(name, name)

        # store consistently
        self.named_vbos[canonical] = vbo

        # and assign to attribute if it exists
        if hasattr(self, canonical):
            setattr(self, canonical, vbo)

        return vbo

    def get_vbo_object(self, name: str) -> "LegacyVBO":
        """Retrieve a VBO by its semantic or shorthand name."""
        canonical = NAME_ALIASES.get(name, name)
        return self.named_vbos.get(canonical)

    def delete(self) -> None:
        for buf in (self.nbo, self.cbo, self.vbo, self.ebo):
            if buf:
                delete_buffer_object(buf)
        self.nbo = self.cbo = self.vbo = self.ebo = None
        self.layout = None

    @property
    def index_count(self) -> int:
        """
        Return the number of indices in the EBO.

        :return: int
        """
        return len(self.ebo.data) if self.ebo and hasattr(self.ebo, "data") else 0

    def draw(self, index_count: int = 0, mode: int = GL_POINTS):
        """
        draw

        :param index_count:
        :param count: int
        :param mode: int
        Enable legacy client states, bind VBOs, draw, and clean up.
        """

        if not index_count:
            index_count = self.index_count
        with self:
            with legacy_client_states(GL_VERTEX_ARRAY, GL_COLOR_ARRAY, GL_NORMAL_ARRAY):
                for vbo in self.named_vbos.values():
                    vbo.bind()
                # Issue draw call
                glDrawArrays(mode, 0, index_count)

    def add_vbo(
            self,
            name: str,
            data: np.ndarray,
            size: int = 3,
            dtype: int = GL_FLOAT,
            handle: int | None = None,
    ) -> Any:
        """Create and register a VBO with explicit parameters."""
        vbo_class = self.get_buffer_class(name)
        if data is None or size <= 0:
            raise ValueError("data must be a numpy array, size > 0")
        vbo = vbo_class(data=data, size=size, handle=handle, dtype=dtype)
        self.add_vbo_object(name, vbo)
        return self

    def get_buffer_class(self, name: str = "vbo") -> type[LegacyVBO]:
        """
        get_buffer_class

        :param name: str
        :return: LegacyVBO
        """
        vbo_class = self.vbo_classes.get(name, LegacyPositionVBO)
        return vbo_class

    def add_ebo(self, name: str = "ebo", data: np.ndarray = None):
        """
        add_ebo

        :param name: str
        :param data: np.ndarray
        """
        ebo_class = self.vbo_classes.get(name, LegacyEBO)
        self.add_vbo_object(name, ebo_class(data=data))

    def draw_elements(
            self,
            count: int = 0,
            mode: int = GL_TRIANGLES,
            dtype: int = GL_UNSIGNED_INT,
            offset: int = 0,
    ):
        """
        Draw using an element buffer (EBO) with legacy client states.

        :param count: Number of indices to draw. Defaults to `self.index_count`.
        :param mode: OpenGL primitive type (GL_TRIANGLES, GL_LINES, etc.).
        :param dtype: Data type of indices (GL_UNSIGNED_BYTE, GL_UNSIGNED_SHORT, GL_UNSIGNED_INT).
        :param offset: Byte offset into the EBO.
        """
        if not self.ebo:
            raise RuntimeError("No element buffer (EBO) bound for draw_elements()")

        if not count:
            count = self.index_count

        # Bind buffers and set up attribute pointers
        with self:
            # Legacy client states still required
            with legacy_client_states(GL_VERTEX_ARRAY, GL_COLOR_ARRAY, GL_NORMAL_ARRAY):
                # Bind each VBO (legacy-style)
                for vbo in self.named_vbos.values():
                    vbo.bind()

                # Bind EBO for indexed drawing
                glBindBuffer(
                    GL_ELEMENT_ARRAY_BUFFER, getattr(self.ebo, "_id", self.ebo)
                )
                glDrawElements(mode, count, dtype, ctypes.c_void_p(offset))
                # Unbind EBO afterwards to prevent accidental reuse
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_layout(self, layout: LayoutDescriptor) -> None:
        self.layout = layout

    def bind(self) -> None:
        """Bind buffers and upload attribute pointers per stored layout."""
        if not self.layout:
            return
        try:
            for attr in self.layout.attributes:
                canonical = NAME_ALIASES.get(attr.name, attr.name)
                vbo = self.named_vbos.get(canonical)
                if not vbo:
                    continue
                # Debug the glBindBuffer call
                buffer_handle = getattr(vbo, "_id", vbo)
                glBindBuffer(GL_ARRAY_BUFFER, buffer_handle)

                # Debug the glEnableVertexAttribArray call
                attr_index = int(attr.index)
                glEnableVertexAttribArray(attr_index)
                # Convert IntConstant to raw int for OpenGL
                # Try multiple ways to extract the integer value from IntConstant
                try:
                    if hasattr(attr.type, "value"):
                        gl_type = attr.type.value
                    elif hasattr(attr.type, "real"):
                        gl_type = attr.type.real
                    else:
                        gl_type = int(attr.type)
                except (ValueError, TypeError):
                    # Fallback: try to access the underlying value directly
                    gl_type = (
                        attr.type.__int__() if hasattr(attr.type, "__int__") else 0x1406
                    )  # GL_FLOAT fallback

                # Ensure offset is properly converted
                offset_ptr = (
                    ctypes.c_void_p(int(attr.offset)) if int(attr.offset) != 0 else None
                )

                glVertexAttribPointer(
                    int(attr.index),
                    int(attr.size),
                    gl_type,
                    bool(attr.normalized),
                    int(attr.stride),
                    offset_ptr,
                )
        except Exception as ex:
            log.error(f"error {ex} occurred in VertexBufferGroup")
            for attr in self.layout.attributes:
                log.parameter("attr", attr)
                log.parameter("attr.index", attr.index)
                log.parameter("attr.size", attr.size)
                log.parameter("attr.type", int(attr.type))
                log.parameter("attr.normalized", attr.normalized)
                log.parameter("attr.stride", attr.stride)

    def unbind(self) -> None:
        """Disable attribute arrays and unbind the array buffer."""
        if not self.layout:
            return
        for attr in self.layout.attributes:
            glDisableVertexAttribArray(attr.index)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
