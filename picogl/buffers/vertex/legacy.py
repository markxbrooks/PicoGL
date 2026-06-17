"""
VertexArrayGroup

Legacy backend (no real GL VAO support)
"""

import ctypes
from typing import Any, Optional, Literal, Union

import numpy as np
from decologr import Decologr as log
from elmo.gl.backend.legacy.primitives.ribbon.model import RibbonAttrs
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    glColorPointer,
    glDrawArrays,
    glDrawElements,
    glEnableClientState,
    glNormalPointer,
    glVertexPointer,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import glBindBuffer

from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.color import LegacyColorVBO
from picogl.backend.legacy.core.vertex.buffer.element import LegacyEBO
from picogl.backend.legacy.core.vertex.buffer.normal import LegacyNormalVBO
from picogl.backend.legacy.core.vertex.buffer.position import LegacyPositionVBO
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.attributes import LayoutDescriptor, AttributeSpec
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer_object
from picogl.buffers.vertex.aliases import (
    NAME_ALIASES,
    VertexArrayRole,
    VertexBufferRole,
)
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.state.client import GLClientState
from picogl.state.draw_mode import GLBufferTarget, GLDataType, GLDrawMode, GLIndexType


class VertexBufferGroup(VertexBase):
    """Container for legacy VBOs, mimicking VAO interface."""

    LEGACY_ATTR_BINDINGS = {
        VertexBufferRole.VBO: (GLClientState.VERTEX, "_vertex_pointer"),
        VertexBufferRole.NBO: (GLClientState.NORMAL, "_normal_pointer"),
        VertexBufferRole.CBO: (GLClientState.COLOR, "_color_pointer"),
    }

    def __init__(self, draw_mode: int = GLDrawMode.LINE_STRIP):
        super().__init__()
        self._index_count = None
        self.handle = 0  # Does absolutely nothing
        self.vao = (
            None  # Bonds Vertex Array Object. Does absolutely nothing, but is needed
        )
        self.vbo: Optional[LegacyPositionVBO | int] = None  # Atom Vertex Buffer Object
        self.cbo: Optional[LegacyColorVBO | int] = None  # Color Vertex Buffer Object
        self.nbo: Optional[LegacyNormalVBO | int] = None  # Normal Vertex Buffer Object
        self.ebo: Optional[LegacyEBO | int] = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None
        self.named_vbos: dict[str, LegacyVBO] = {}  # store by semantic name
        self.draw_mode: int = draw_mode
        self.vbo_classes = {
            RibbonAttrs.VBO: LegacyPositionVBO,
            RibbonAttrs.CBO: LegacyColorVBO,
            RibbonAttrs.EBO: LegacyEBO,
            RibbonAttrs.NBO: LegacyNormalVBO,
        }

    def __del__(self):
        # Don't auto-delete OpenGL resources here unless you are certain the GL context is current.
        # Logging here can help detect premature GC.
        # print("VertexBufferGroup.__del__", self)
        pass

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
        if self._index_count is not None:
            return self._index_count
        return len(self.ebo.data) if self.ebo and hasattr(self.ebo, "data") else 0

    @index_count.setter
    def index_count(self, value):
        """Setter for index_count with basic validation."""
        if not isinstance(value, int):
            raise TypeError(f"index_count must be an int, got {type(value).__name__}")
        if value < 0:
            raise ValueError("index_count must be non-negative")
        self._index_count = value

    def draw(self, index_count: int = 0, mode: int = GLDrawMode.POINTS):
        """
        draw

        :param index_count:
        :param count: int
        :param mode: int
        Enable legacy client states, bind VBOs, draw, and clean up.
        """

        if not index_count:
            index_count = self.index_count
        if not mode:
            mode = self.draw_mode

        # Use the layout-based binding approach
        with self:
            with legacy_client_states(GLClientState.VERTEX, GLClientState.COLOR, GLClientState.NORMAL):
                # Issue draw call
                self._draw_arrays(index_count, mode)

    def add_vbo(
        self,
        name: str,
        data: np.ndarray,
        size: int = 3,
        dtype: int = GLDataType.FLOAT,
        handle: int | None = None,
    ) -> Any:
        """Create and register a VBO with explicit parameters."""
        vbo_class = self.get_buffer_class(name)
        if data is None or size <= 0:
            raise ValueError("data must be a numpy array, size > 0")
        vbo = vbo_class(data=data, size=size, handle=handle, dtype=dtype)
        self.add_vbo_object(name, vbo)
        return self

    def get_buffer_class(self, name: str = VBOType.VBO) -> type[LegacyVBO]:
        """
        get_buffer_class

        :param name: str
        :return: LegacyVBO
        """
        vbo_class = self.vbo_classes.get(name, LegacyPositionVBO)
        return vbo_class

    def add_ebo(self, name: str = VBOType.EBO, data: np.ndarray = None):
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
        mode: int = GLDrawMode.TRIANGLES,
        dtype: int = GLIndexType.UNSIGNED_INT,
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
            with legacy_client_states(GLClientState.VERTEX, GLClientState.COLOR, GLClientState.NORMAL):
                # Bind each VBO (legacy-style)
                for vbo in self.named_vbos.values():
                    vbo.bind()
                self._draw_elements(count, dtype, mode, offset)

    def _bind_ebo(self):
        # Indexed draws need an EBO; array-only geometry (ribbons, coils, etc.) does not.
        if not self.ebo:
            return
        ebo_id = getattr(self.ebo, "handle", None)
        if ebo_id is None:
            ebo_id = getattr(self.ebo, "_id", None)
        if ebo_id is None:
            raise RuntimeError("EBO has no GL buffer name (handle/_id)")
        self._bind_ebo_id(ebo_id)

    def _bind_ebo_id(self, ebo_id: Any | None):
        self._bind_buffer(GLBufferTarget.ELEMENT, ebo_id)

    def _draw_arrays(self, index_count: int, mode: int):
        glDrawArrays(mode, 0, index_count)

    def _unbind_ebo(self):
        self._bind_ebo_id(0)

    def _draw_elements(self, count: int, dtype: int, mode: int, offset: int):
        glDrawElements(mode, count, dtype, ctypes.c_void_p(offset))

    def _bind_buffer(self, target, ebo_id: Any | None):
        glBindBuffer(target, ebo_id)

    def set_layout(self, layout: LayoutDescriptor) -> None:
        self.layout = layout

    def bind(self) -> None:
        """Bind buffers and configure legacy OpenGL client arrays."""
        if not self.layout:
            return

        try:
            for attr in self.layout.attributes:
                name = attr.name
                if isinstance(name, VertexBufferRole):
                    role = name
                else:
                    key = name.lower() if isinstance(name, str) else str(name).lower()
                    role = NAME_ALIASES.get(name, NAME_ALIASES.get(key, key))
                vbo = self.named_vbos.get(role)

                if not vbo:
                    continue

                buffer_handle = getattr(vbo, VertexArrayRole.VAO, vbo)
                self._bind_buffer(GLBufferTarget.ARRAY, buffer_handle)

                binding = self.LEGACY_ATTR_BINDINGS.get(role)

                if binding:
                    state, pointer_method = binding
                    self._legacy_client_state(state)
                    getattr(self, pointer_method)(attr)
            self._bind_ebo()

        except Exception as ex:
            log.error(f"error {ex} occurred in VertexBufferGroup")
            for attr in self.layout.attributes:
                log.parameter("attr", attr)
                log.parameter("attr.index", attr.index)
                log.parameter("attr.size", attr.size)
                log.parameter("attr.type", int(attr.type))
                log.parameter("attr.normalized", attr.normalized)
                log.parameter("attr.stride", attr.stride)

    def _color_pointer(self, attr: AttributeSpec):
        glColorPointer(attr.size, attr.type, attr.stride, ctypes.c_void_p(attr.offset))

    def _normal_pointer(self, attr: AttributeSpec):
        glNormalPointer(attr.type, attr.stride, ctypes.c_void_p(attr.offset))

    def _vertex_pointer(self, attr: AttributeSpec):
        glVertexPointer(attr.size, attr.type, attr.stride, ctypes.c_void_p(attr.offset))

    def _legacy_client_state(self, state: GLClientState):
        glEnableClientState(state)

    def unbind(self) -> None:
        """Disable attribute arrays and unbind the array buffer."""
        if not self.layout:
            return
        # For legacy rendering, we don't need to disable vertex attrib arrays
        # since we're using the old glVertexPointer approach
        self._bind_buffer(GLBufferTarget.ARRAY, 0)
        self._unbind_ebo()

    def __enter__(self):
        """Context manager entry - bind the VBO."""
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - unbind the VBO."""
        self.unbind()
