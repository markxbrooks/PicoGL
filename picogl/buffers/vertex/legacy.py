"""
This module provides the VertexBufferGroup class, which is a container for legacy
VBOs that mimics the VAO interface. It supports the creation, management, binding,
and drawing of vertex buffer objects (VBOs) and element buffer objects (EBOs).

Classes:
- VertexBufferGroup: Manages various VBOs and provides functionality for
  adding, accessing, and drawing vertex buffer data.
"""

from typing import Any, Optional

import numpy as np
from decologr import Decologr as log

from picogl.attrs.model import VBOAttrs
from picogl.backend.legacy.core.vertex.buffer.client_states import legacy_client_states
from picogl.backend.legacy.core.vertex.buffer.color import LegacyColorVBO
from picogl.backend.legacy.core.vertex.buffer.element import LegacyEBO
from picogl.backend.legacy.core.vertex.buffer.normal import LegacyNormalVBO
from picogl.backend.legacy.core.vertex.buffer.position import LegacyPositionVBO
from picogl.backend.legacy.core.vertex.buffer.vertex import LegacyVBO
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import delete_buffer_object
from picogl.buffers.vertex.aliases import NAME_ALIASES, VertexBufferRole
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.state.client import GLClientState
from picogl.state.draw_mode import GLBufferTarget, GLDataType, GLDrawMode
from picogl.wrappers.buffer import gl_bind_buffer
from picogl.wrappers.client_state import gl_enable_legacy_client_state
from picogl.wrappers.draw import gl_draw_arrays, gl_draw_elements


class VertexBufferGroup(VertexBase):
    """Container for legacy VBOs, mimicking VAO interface."""

    LEGACY_ATTR_BINDINGS = {
        VertexBufferRole.VBO: (GLClientState.VERTEX, "_vertex_pointer"),
        VertexBufferRole.NBO: (GLClientState.NORMAL, "_normal_pointer"),
        VertexBufferRole.CBO: (GLClientState.COLOR, "_color_pointer"),
    }

    def __init__(self, draw_mode: GLDrawMode = GLDrawMode.LINE_STRIP):
        super().__init__()
        self._index_count = None
        self.handle = 0  # compat shim, not a real VAO handle
        # self.vao = None  # compat shim, not a real VAO
        self.layout: Optional[LayoutDescriptor] = None
        self.named_vbos: dict[VertexBufferRole | str, LegacyVBO] = {}
        self.draw_mode: GLDrawMode = draw_mode
        self.vbo_classes = {
            VBOAttrs.VBO: LegacyPositionVBO,
            VBOAttrs.CBO: LegacyColorVBO,
            VBOAttrs.EBO: LegacyEBO,
            VBOAttrs.NBO: LegacyNormalVBO,
        }

    def __del__(self):
        # Don't auto-delete OpenGL resources here unless you are certain the gl context is current.
        # Logging here can help detect premature GC.
        # print("VertexBufferGroup.__del__", self)
        pass

    @property
    def vbo(self) -> Optional[LegacyPositionVBO | int]:
        return self.named_vbos.get(VertexBufferRole.VBO)

    @vbo.setter
    def vbo(self, value: Optional[LegacyPositionVBO | int]) -> None:
        self._set_named_vbo(VertexBufferRole.VBO, value)

    @property
    def cbo(self) -> Optional[LegacyColorVBO | int]:
        return self.named_vbos.get(VertexBufferRole.CBO)

    @cbo.setter
    def cbo(self, value: Optional[LegacyColorVBO | int]) -> None:
        self._set_named_vbo(VertexBufferRole.CBO, value)

    @property
    def nbo(self) -> Optional[LegacyNormalVBO | int]:
        return self.named_vbos.get(VertexBufferRole.NBO)

    @nbo.setter
    def nbo(self, value: Optional[LegacyNormalVBO | int]) -> None:
        self._set_named_vbo(VertexBufferRole.NBO, value)

    @property
    def ebo(self) -> Optional[LegacyEBO | int]:
        return self.named_vbos.get(VertexBufferRole.EBO)

    @ebo.setter
    def ebo(self, value: Optional[LegacyEBO | int]) -> None:
        self._set_named_vbo(VertexBufferRole.EBO, value)

    def _set_named_vbo(
        self, role: VertexBufferRole, value: Optional[LegacyVBO | int]
    ) -> None:
        if value is None:
            self.named_vbos.pop(role, None)
        else:
            self.named_vbos[role] = value

    def add_vbo_object(self, name: str, vbo: "LegacyVBO") -> "LegacyVBO":
        """Register a VBO by semantic name or shorthand alias."""
        canonical = NAME_ALIASES.get(name, name)
        self.named_vbos[canonical] = vbo
        return vbo

    def get_vbo_object(self, name: str) -> "LegacyVBO":
        """Retrieve a VBO by its semantic or shorthand name."""
        canonical = NAME_ALIASES.get(name, name)
        return self.named_vbos.get(canonical)

    def delete(self) -> None:
        for buf in self.named_vbos.values():
            if buf:
                delete_buffer_object(buf)
        self.named_vbos.clear()
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

    def draw(self, index_count: int = 0, mode: GLDrawMode | None = None):
        """
        draw

        :param index_count: int
        :param mode: int
        Enable legacy client states, bind VBOs, draw, and clean up.
        """
        if not index_count:
            index_count = self.index_count
        if mode is None:
            mode = self.draw_mode

        with self:
            with legacy_client_states(*self._resolve_client_states()):
                if self.ebo is not None:
                    gl_draw_elements(index_count=index_count, mode=mode)
                    return
                gl_draw_arrays(index_count=index_count, mode=mode)

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

    def _bind_ebo(self):
        # Indexed draws need an EBO; array-only geometry (ribbons, coils, etc.) does not.
        if not self.ebo:
            return
        ebo_id = getattr(self.ebo, "handle", None)
        if ebo_id is None:
            ebo_id = getattr(self.ebo, "_id", None)
        if ebo_id is None:
            raise RuntimeError("EBO has no gl buffer name (handle/_id)")
        self._bind_ebo_id(ebo_id)

    def _bind_ebo_id(self, ebo_id: Any | None):
        gl_bind_buffer(GLBufferTarget.ELEMENT, ebo_id)

    def _unbind_ebo(self):
        self._bind_ebo_id(0)

    def set_layout(self, layout: LayoutDescriptor) -> None:
        self.layout = layout

    def _resolve_client_states(self) -> tuple[GLClientState, ...]:
        """Return legacy client states to enable for the current layout."""
        if not self.layout:
            return (
                GLClientState.VERTEX,
                GLClientState.COLOR,
                GLClientState.NORMAL,
            )

        states: list[GLClientState] = []
        seen: set[GLClientState] = set()
        for attr in self.layout.attributes:
            role = attr.role
            binding = self.LEGACY_ATTR_BINDINGS.get(role)
            if binding is None or self.named_vbos.get(role) is None:
                continue
            state = binding[0]
            if state not in seen:
                seen.add(state)
                states.append(state)

        if not states:
            return (
                GLClientState.VERTEX,
                GLClientState.COLOR,
                GLClientState.NORMAL,
            )
        return tuple(states)

    def _buffer_handle(self, vbo: LegacyVBO | int) -> int:
        if isinstance(vbo, int):
            return vbo
        handle = getattr(vbo, "handle", None)
        if handle is None:
            handle = getattr(vbo, "_id", None)
        if handle is None:
            raise RuntimeError(f"VBO has no gl buffer name (handle/_id): {vbo!r}")
        return handle

    def bind(self) -> None:
        """Bind buffers and configure legacy OpenGL client arrays."""
        self._do_binding()

    def _do_binding(self):
        """do binding"""
        if not self.layout:
            return
        try:
            for attr in self.layout.attributes:
                role = attr.role
                vbo = self.named_vbos.get(role)
                if vbo is None:
                    continue

                gl_bind_buffer(GLBufferTarget.ARRAY, self._buffer_handle(vbo))

                binding = self.LEGACY_ATTR_BINDINGS.get(role)
                if not binding:
                    continue

                state, fn_name = binding
                gl_enable_legacy_client_state(state)
                getattr(self, fn_name)(attr)
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

    def unbind(self) -> None:
        """Disable attribute arrays and unbind the array buffer."""
        if not self.layout:
            return
        self._do_unbinding()

    def _do_unbinding(self):
        # For legacy rendering, we don't need to disable vertex attrib arrays
        # since we're using the old glVertexPointer approach
        gl_bind_buffer(GLBufferTarget.ARRAY, 0)
        self._unbind_ebo()

    def __enter__(self):
        """Context manager entry - bind the VBO."""
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - unbind the VBO."""
        self.unbind()
