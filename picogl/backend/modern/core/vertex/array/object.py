"""
vertex_array_object.py

This module defines the `VertexArrayObject` class, which encapsulates the creation, management,
and usage of OpenGL Vertex Array Objects (VAOs) in modern OpenGL rendering workflows.

The `VertexArrayObject` class inherits from `VertexBuffer` and provides
a clean, object-oriented interface for managing VAO handles and vertex
attribute configurations.

It supports binding/unbinding operations,
attribute registration, and rendering via `glDrawArrays`.

Features:
- Automatic VAO generation if none is provided
- Storage and enabling of vertex attribute definitions
- Integration with VBOs via `ModernVBO` (used as context managers)
- Simplified draw calls for points or other primitive modes
- Graceful deletion and handle management

Dependencies:
- numpy
- PyOpenGL (OpenGL.GL and OpenGL.raw.GL)

Intended for OpenGL 3.0+ with VAO support.

"""

import sys
from contextlib import contextmanager, nullcontext
from typing import Any, Optional, Union

import numpy as np

from decologr import Decologr as log
from picogl.backend.modern.core.vertex.array.draw_spec import DrawSpec
from picogl.backend.modern.core.vertex.attribute import VertexAttribute
from picogl.backend.gl.api import gl_draw_arrays_spec, gl_draw_elements_spec
from picogl.backend.gl.api.glcleanup import gl_delete_buffers, gl_delete_vertex_arrays
from picogl.backend.gl.api.vertex.arrays.bind import gl_bind_vertex_array
from picogl.backend.gl.api.vertex.arrays.check_is import gl_is_vertex_array
from picogl.backend.gl.api.vertex.arrays.generate import gl_gen_vertex_arrays
from picogl.backend.gl.api.vertex.attrib_pointer import gl_vertex_attrib_pointer, gl_enable_vertex_array_attributes
from picogl.backend.gl.api.vertex.enable_array import gl_enable_vertex_array
from picogl.backend.gl.enums import (
    GLDrawMode,
    GLUsageHint,
)
from picogl.backend.modern.core.vertex.array.helpers import point_rendering
from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.gpu.buffers.attributes import AttributeSpec, LayoutDescriptor
from picogl.gpu.buffers.base import VertexBase
from picogl.gpu.buffers.vertex.aliases import NAME_ALIASES, VertexBufferRole
from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType
from picogl.safe import gl_gen_safe

# PicoGL must not import ElMo or PySide6 at module load (GLUT examples stay Qt-free).
SILENT_VAO = True


def _qopengl_context_class() -> Any | None:
    """Return QOpenGLContext only if PySide6.QtGui is already imported."""
    qtgui = sys.modules.get("PySide6.QtGui")
    if qtgui is None:
        return None
    return getattr(qtgui, "QOpenGLContext", None)


def _current_qt_gl_context() -> Any | None:
    qctx = _qopengl_context_class()
    if qctx is None:
        return None
    try:
        return qctx.currentContext()
    except Exception:
        return None

def current_gl_context() -> int | None:
    try:
        ctx = _current_qt_gl_context()
        return id(ctx) if ctx is not None else None
    except Exception:
        return None


def _is_element_attribute(attr: AttributeSpec) -> bool:
    """Return True when *attr* describes an element buffer, not a vertex attribute.

    Index buffers are bound via :meth:`VertexArrayObject.add_ebo`, not as VBOs.
    Layouts such as ``setup_bond_layout()`` still list EBO for documentation;
    ``set_layout`` must skip them instead of requiring a vertex buffer.
    """
    if getattr(attr, "role", None) == VertexBufferRole.EBO:
        return True
    if getattr(attr, "vbo_type", None) == VBOType.EBO:
        return True
    name = getattr(attr, "name", None)
    return name in (VBOType.EBO, VertexBufferRole.EBO, "ebo", "indices", "elements")


class GLResource:
    """Base class for all gl-owned objects."""

    def __init__(self, handle):
        self._creation_context = _current_qt_gl_context()
        self._deleted = False
        self._handle = None

    @property
    def context(self):
        return self._creation_context

    def validate_context(self):
        if _qopengl_context_class() is None:
            return
        ctx = _current_qt_gl_context()

        if ctx is None:
            raise RuntimeError("No current gl context")

        if self._creation_context is None:
            raise RuntimeError("Resource has no creation context")

        if ctx is not self._creation_context:
            raise RuntimeError(
                f"Context mismatch: created in {self._creation_context}, current {ctx}"
            )



class VertexArrayObject(VertexBase, GLResource):
    """
    OpenGL Vertex Array Objects (VAO) class
    """

    def __init__(self, handle: int = None, *, registry_label: Optional[str] = None):
        """
        VertexArrayObject

        :param handle: int Handle (ID) of the OpenGL Vertex Array Object (VAO).
        :param registry_label: Optional custom label for :func:`store_in_gl_registry`
            (defaults to ``self.__class__.__name__``).
        """
        self._creation_context = _current_qt_gl_context()
        log.message(
            f"VAO context :{id(self._creation_context)}",
            scope="VertexArrayObject",
            silent=SILENT_VAO,
        )
        self._registry_label = registry_label
        self._configured: bool = False
        if not handle or handle is None:
            if gl_gen_vertex_arrays():
                handle = gl_gen_safe(gl_gen_vertex_arrays())
            else:
                raise RuntimeError(
                    "glGenVertexArrays not available — OpenGL context not ready"
                )
        super().__init__(handle)
        self.attributes: list[AttributeSpec] = []
        self.vbos = []
        self.named_vbos: dict[str, VertexBuffer] = {}
        self._vbos_by_attribute: dict[int, ModernVBO] = {}
        self.ebo = None  # Bond Index Buffer Object
        self.layout: Optional[LayoutDescriptor] = None
        self.bind()

    def build(
        self,
        attributes: list[VertexAttribute],
        indices: np.ndarray | None = None,
    ) -> None:
        """Populate self from attribute arrays and an optional element buffer."""
        for attribute in attributes:
            self.add_vbo(spec=attribute.spec, data=attribute.data)
        if indices is not None:
            self.add_ebo(data=np.asarray(indices))

    def is_valid_in_current_context(self) -> bool:
        if _qopengl_context_class() is None:
            return True
        ctx = _current_qt_gl_context()

        # GLUT / non-Qt: PySide6 may be installed but no QOpenGLContext is current.
        # Resources created and used there have _creation_context is None.
        if self._creation_context is None and ctx is None:
            return True

        if ctx is None:
            return False

        # Fast path: correct context
        if ctx is self.context:
            return True

        # Optional fallback: gl-level validation (ONLY if sharing contexts exist)
        try:
            handle = getattr(self, "handle", None)
            if handle:
                return bool(gl_is_vertex_array(handle))
        except Exception:
            return False

        return False

    def set_layout(self, layout: LayoutDescriptor | None) -> None:
        """Configure the VAO from a layout descriptor."""
        if layout is None or self._configured:
            return

        with self.bound():
            self.layout = layout

            if self.ebo:
                self.ebo.bind()

            for attr in layout.attributes:
                if _is_element_attribute(attr):
                    continue

                vbo = self.get_vbo_object(attr.name)
                if vbo is None:
                    vbo = self._vbos_by_attribute.get(attr.index)

                if vbo is None:
                    raise RuntimeError(f"No VBO bound for attribute '{attr.name}'")

                vbo.bind()
                gl_enable_vertex_array_attributes(attr)

            self._configured = True

    @contextmanager
    def bound(self):
        if not self.bind():
            raise RuntimeError("Failed to bind VAO")
        try:
            yield
        finally:
            self.unbind()

    def bind(self) -> Union["VertexArrayObject", None]:
        """
        Bind the VAO for use in rendering.
        :return: True if bound, False if skipped (wrong context — avoids GL_INVALID_OPERATION/segfault).
        """
        if not self.is_valid_in_current_context():
            log.error(
                "VAO created in different gl context; skipping bind to avoid invalid operation",
                scope=self.__class__.__name__,
            )
            return None
        gl_bind_vertex_array(self.handle)
        return self

    def unbind(self):
        """
        Unbind the VAO by binding to zero.
        """
        gl_bind_vertex_array(0)

    def delete(self):
        """
        Delete the VAO from GPU memory.
        """
        if self.handle is not None and int(self.handle) > 0:
            gl_delete_vertex_arrays(int(self.handle))
            self.handle = 0

    def configure(self):
        """set layout"""
        self.set_layout(self.layout)

    def add_vbo_object(self, name: str, vbo: "ModernVBO") -> "ModernVBO":
        """Register a VBO by semantic name or shorthand alias."""
        # normalize to canonical key
        canonical = NAME_ALIASES.get(name, name)
        if not isinstance(vbo, VertexBuffer):
            raise TypeError(f"Expected VertexBuffer, got {type(vbo)}")

        # store consistently
        self.named_vbos[canonical] = vbo

        # and assign to attribute if it exists
        if hasattr(self, canonical):
            setattr(self, canonical, vbo)

        return vbo

    def get_vbo_object(self, name: str) -> VertexBuffer | None:
        """Retrieve a VBO by its semantic or shorthand name."""
        canonical = NAME_ALIASES.get(name, name)
        return self.named_vbos.get(canonical)

    def add_vbo(
        self,
        spec: AttributeSpec,
        data: np.ndarray,
        *,
        handle: int | None = None,
    ) -> ModernVBO:
        """Add a vertex buffer and configure its vertex attribute.

        :param spec: Vertex attribute layout (index, size, dtype, name).
        :param data: Vertex data uploaded into the VBO.
        :param handle: Optional existing OpenGL buffer handle.
        :return: The created :class:`ModernVBO`.
        """
        vbo = ModernVBO(handle=handle)
        vbo.bind()
        vbo.set_data(data)
        vbo.set_vertex_attributes(
            index=spec.index,
            data=data,
            size=spec.size,
            dtype=spec.dtype,
            normalized=spec.normalized,
            stride=spec.stride,
            offset=spec.offset,
        )
        vbo.configure()
        self.attributes.append(spec)
        self.vbos.append(vbo)
        self._vbos_by_attribute[spec.index] = vbo
        self.add_vbo_object(spec.name, vbo)
        return vbo

    def delete_buffers(self):
        """
        delete_buffers

        :return: None
        """
        for vbo in self.vbos:
            gl_delete_buffers(vbo)
        self.vbos.clear()
        self.attributes.clear()
        self._vbos_by_attribute.clear()

        if self.ebo:
            gl_delete_buffers(self.ebo)
            self.ebo = None

        self.named_vbos.clear()

    def add_ebo(self, data: np.ndarray) -> ModernEBO:
        """
        add_ebo

        :param data: np.ndarray
        :return: int
        """
        ebo = ModernEBO(data=data)
        ebo.bind()
        ebo.set_element_attributes(
            data=data, size=data.nbytes, dtype=GLUsageHint.STATIC_DRAW
        )
        ebo.configure()
        self.ebo = ebo
        return ebo

    def set_ebo(self, ebo: int) -> int:
        """
        add_ebo

        :param ebo: int
        :return: int
        """
        self.ebo = ModernEBO(handle=ebo)
        self.ebo.bind()
        return ebo

    @property
    def index_count(self) -> int | None:
        """
        Return the number of indices in the EBO.

        :return: int
        """
        try:
            if self.ebo:
                if hasattr(self.ebo, "data"):
                    return len(self.ebo.data)
            return 0
        except Exception as ex:
            log.error(f"error {ex} occurred")

    def data_length(self) -> int:
        """Number of vertices in the position buffer, or indices if no positions."""
        from picogl.gpu.buffers.length import length_from_vbo
        from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
        from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType

        for key in (VBOType.VBO, VertexBufferRole.VBO):
            count = length_from_vbo(self.named_vbos.get(key))
            if count > 0:
                return count
        for vbo in self.vbos:
            count = length_from_vbo(vbo)
            if count > 0:
                return count
        idx = self.index_count
        return int(idx) if idx else 0

    def draw(self, spec: DrawSpec | None = None) -> None:
        """Issue ``glDrawArrays`` or ``glDrawElements`` from a :class:`DrawSpec`.

        ``spec.count is None`` uses :attr:`index_count`. An explicit ``count=0``
        is a no-op and does not fall back to the element buffer length.

        :param spec: GPU draw command; defaults to :class:`DrawSpec` (POINTS).
        """
        spec = spec or DrawSpec(count=self.index_count)
        spec.count = self.index_count if spec.count is None else spec.count
        if not spec.count:
            return

        context = (
            point_rendering()
            if spec.mode == GLDrawMode.POINTS
            else nullcontext()
        )

        with context, self.bound():
            if self.ebo:
                self.ebo.bind()
                gl_draw_elements_spec(spec)
            else:
                gl_draw_arrays_spec(spec)

    def _modern_vbo_for_attrib(self, attrib_index: int) -> Optional[ModernVBO]:
        """Return the :class:`ModernVBO` created for attribute ``attrib_index``."""
        return self._vbos_by_attribute.get(attrib_index)

    def update_vbo(self, index: int, data: np.ndarray) -> None:
        """update vbo"""
        if data is None:
            raise TypeError("update_vbo: data must be a numpy array")
    
        vbo = self._modern_vbo_for_attrib(index)
        if vbo is None:
            log.warning(
                f"update_vbo: no ModernVBO for attribute index {index}",
                scope=self.__class__.__name__,
            )
            return
    
        with self.bound():
            with vbo:
                vbo.update(data)

    
