"""
Axes visualization for crystallographic structures.

This module provides functionality to render coordinate axes
as colored lines with labels.
"""
from typing import Optional

import numpy as np

from elmo.gl.backend.legacy.gizmos.axes.setup import setup_buffers_from_mesh_data
from elmo.gl.renderers.gizmos.cartesian_axes import CartesianAxesRenderer
from elmo.xtal.unit_cell_coords import UnitCellCoordinateGenerator
from OpenGL import GL
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_12, glutBitmapCharacter, glutInit

from picogl.backend.legacy.gizmos.axes.array import AxesVBG
from picogl.logger import Logger as log
from picogl.renderer import MeshData

# Initialize GLUT once when the module is imported
try:
    glutInit()
    log.info("✅ GLUT _initialized successfully for text rendering")
except Exception as e:
    log.warning(f"⚠️ GLUT initialization failed: {e}. Text labels will be disabled.")
    GLUT_AVAILABLE = False
else:
    GLUT_AVAILABLE = True


class LegacyCartesianAxesRenderer(CartesianAxesRenderer):
    """
    Simple renderer for X/Y/Z axes as coloured lines with optional text labels.
    X = red, Y = green, Z = blue.
    """

    def __init__(self):
        super().__init__()
        self.mesh_data: Optional[MeshData] = None
        self.mesh_vbg: Optional[AxesVBG] = None

        # user-tunable
        self.visible: bool = True
        self.show_labels: bool = True
        self.line_width: float = 2.0
        self.axis_length: float = 50.0
        self.label_offset: float = 5.0

        # bookkeeping
        self.vertices: Optional[np.ndarray] = None
        self.colors: Optional[np.ndarray] = None
        self._initialized: bool = False

        # coordinate generator for lattice frames etc.
        self.coord_generator = UnitCellCoordinateGenerator()

    # ------------------------------------------------------------------ utils
    def is_ready(self) -> bool:
        """True if buffers are built and renderer visible."""
        return self._initialized and self.visible and self.mesh_vbg and self.vertices is not None

    # ---------------------------------------------------------------- init/destroy
    def initialize(self) -> None:
        """Allocate buffers & layout for the axes."""
        if self._initialized:
            return
        self.gl_get_error()
        if self.mesh_data is None:
            log.error("Missing mesh data for axes")
            return
        try:
            self.mesh_vbg = setup_buffers_from_mesh_data(self.mesh_data, cls=AxesVBG)
            self._initialized = True
            log.info("Axes buffers initialised")
        except Exception as exc:
            log.error(f"Axes buffer initialisation failed: {exc}")
            self._initialized = False
            self.gl_get_error()

    def cleanup(self) -> None:
        """Release GL buffers."""
        try:
            if self.mesh_vbg and hasattr(self.mesh_vbg, "delete"):
                try:
                    self.mesh_vbg.delete()
                except Exception as e:
                    log.warning(f"Failed to delete VBG: {e}")
        finally:
            self.mesh_data = None
            self.mesh_vbg = None
            self.vertices = None
            self.colors = None
            self._initialized = False
            log.info("Axes resources cleaned")

    # ---------------------------------------------------------------- rendering
    def render(self, mvp_matrix: Optional[np.ndarray] = None) -> None:
        """Draw axes lines, plus optional labels."""
        if not self.is_ready():
            return
        self._set_gl_state()
        try:
            self.mesh_vbg.draw()
        except Exception as exc:
            log.error(f"Axes draw failed: {exc}")
            self._render_immediate_fallback()
        finally:
            if self.show_labels:
                try:
                    self._render_labels()
                except Exception as exc:
                    log.warning(f"Axes label draw failed: {exc}")
            self._restore_gl_state()

    # ---------------------------------------------------------------- labels
    def _render_labels(self) -> None:
        """_render_labels."""
        if not GLUT_AVAILABLE:
            self._render_fallback_indicators()
            return
        GL.glColor3f(1.0, 1.0, 1.0)
        self._render_text_label("X", self.axis_length + self.label_offset, 0, 0)
        self._render_text_label("Y", 0, self.axis_length + self.label_offset, 0)
        self._render_text_label("Z", 0, 0, self.axis_length + self.label_offset)

    def _render_text_label(self, text: str, x: float, y: float, z: float) -> None:
        """_render_text_label(text, x, y, z)"""
        GL.glRasterPos3f(x, y, z)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    def _render_fallback_indicators(self) -> None:
        """render_fallback_indicators."""
        GL.glColor3f(1, 0, 0); self._render_axis_indicator(self.axis_length + self.label_offset, 0, 0)
        GL.glColor3f(0, 1, 0); self._render_axis_indicator(0, self.axis_length + self.label_offset, 0)
        GL.glColor3f(0, 0, 1); self._render_axis_indicator(0, 0, self.axis_length + self.label_offset)

    def _render_axis_indicator(self, x: float, y: float, z: float) -> None:
        """Draw a small cross at the endpoint."""
        s = 2.0
        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(x - s, y, z); GL.glVertex3f(x + s, y, z)
        GL.glVertex3f(x, y - s, z); GL.glVertex3f(x, y + s, z)
        GL.glEnd()

    def gl_get_error(self):
        """gl get error."""
        try:
            GL.glGetError()  # flush errors to catch context issues
        except Exception as exc:
            log.error(f"OpenGL context unavailable: {exc}")
            return

