"""
GLRaster Driver

Cached write-only raster state. Imperative setters implement gl calls;
`apply(RasterState)` diffs frozen snapshots and is the preferred API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from OpenGL.GL import (GL_POINT_SIZE_RANGE, glGetFloatv, glLineWidth,
                       glPointSize, glPolygonMode)
from OpenGL.raw.GL.VERSION.GL_1_1 import glPolygonOffset

from picogl.backend.gl.driver.applicable_state import ApplicableState
from picogl.backend.gl.state.fill import GLFace, GLFillMode
from picogl.backend.state import gl_value

if TYPE_CHECKING:
    from picogl.backend.state import RasterState


def resolve_polygon_mode_args(*args: Any) -> tuple[Any, Any]:
    """Normalize set_polygon_mode overloads to (face, mode)."""
    if len(args) == 1:
        return GLFace.FRONT_AND_BACK, args[0]
    if len(args) == 2:
        return args[0], args[1]
    raise TypeError("set_polygon_mode expects mode or face, mode")


def _gl_set_polygon_mode(face_val: int, mode_val: int) -> None:
    """Issue a raw glPolygonMode call without touching driver cache."""
    glPolygonMode(face_val, mode_val)


class GLRasterDriver(ApplicableState):
    """Fixed-function raster state with write-only gl and cached current values."""

    _shared: Optional["GLRasterDriver"] = None

    @classmethod
    def shared(cls) -> GLRasterDriver | None:
        """Process-wide raster driver for legacy class-level call sites."""
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    def _is_same(self, old, new) -> bool:
        return (
            old.line_width == new.line_width
            and old.polygon_mode == new.polygon_mode
            and old.polygon_offset == new.polygon_offset
            and old.point_size == new.point_size
        )

    def __init__(self):
        super().__init__()
        self._line_width: float = 1.0
        self._polygon_mode: tuple[int, int] = (GLFillMode.FILL, GLFillMode.FILL)
        self._point_size: Optional[float] = None
        self._polygon_offset: tuple[float, float] = (0.0, 0.0)
        self._point_size_range: Optional[tuple[float, float]] = None
        self._current: Optional["RasterState"] = None

    def set_line_width(self, width: float) -> None:
        width = float(width)
        if self._line_width == width:
            return
        glLineWidth(width)
        self._line_width = width

    def get_line_width(self) -> float:
        return self._line_width

    def set_point_size(self, size: float) -> None:
        size = float(size)
        if self._point_size == size:
            return
        glPointSize(size)
        self._point_size = size

    def get_point_size_range(self) -> tuple[float, float] | None:
        if self._point_size_range is None:
            min_size, max_size = glGetFloatv(GL_POINT_SIZE_RANGE)
            self._point_size_range = (float(min_size), float(max_size))
        return self._point_size_range

    def set_clamped_point_size(self, size: float) -> None:
        min_size, max_size = self.get_point_size_range()
        self.set_point_size(max(min_size, min(max_size, float(size))))

    def get_polygon_mode(self):
        """Return cached front/back polygon modes (same shape as glGetIntegerv(GL_POLYGON_MODE))."""
        import numpy as np

        return np.array(self._polygon_mode, dtype=np.int32)

    def set_polygon_offset(self, factor: float, units: float) -> None:
        offset = (float(factor), float(units))
        if self._polygon_offset == offset:
            return
        glPolygonOffset(offset[0], offset[1])
        self._polygon_offset = offset

    def set_polygon_mode(self, *args) -> None:
        face, mode = resolve_polygon_mode_args(*args)
        face_val = gl_value(face)
        mode_val = int(gl_value(mode))
        front_mode, back_mode = self._polygon_mode

        if face_val == gl_value(GLFace.FRONT_AND_BACK):
            if front_mode == mode_val and back_mode == mode_val:
                return
            _gl_set_polygon_mode(face_val, mode_val)
            self._polygon_mode = (mode_val, mode_val)
            return

        if face_val == gl_value(GLFace.FRONT):
            if front_mode == mode_val:
                return
            _gl_set_polygon_mode(face_val, mode_val)
            self._polygon_mode = (mode_val, back_mode)
            return

        if face_val == gl_value(GLFace.BACK):
            if back_mode == mode_val:
                return
            _gl_set_polygon_mode(face_val, mode_val)
            self._polygon_mode = (front_mode, mode_val)
            return

        _gl_set_polygon_mode(face_val, mode_val)

    def _do_apply(self, state: RasterState, prev: RasterState):
        if prev is None or prev.line_width != state.line_width:
            self.set_line_width(state.line_width)

        if prev is None or prev.polygon_mode != state.polygon_mode:
            self.set_polygon_mode(GLFace.FRONT_AND_BACK, gl_value(state.polygon_mode))

        if prev is None or prev.polygon_offset != state.polygon_offset:
            self.set_polygon_offset(*state.polygon_offset)

        if state.point_size is not None and (
            prev is None or prev.point_size != state.point_size
        ):
            self.set_point_size(state.point_size)


def shared_raster_driver() -> GLRasterDriver | None:
    """Backward-compatible alias for :meth:`GLRasterDriver.shared`."""
    return GLRasterDriver.shared()
