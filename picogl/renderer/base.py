"""
RendererBase is a base class for rendering operations, providing foundational
methods for initializing rendering states, managing OpenGL features, and
dispatching rendering tasks.

This module implements essential rendering functionality and acts as a
common base for custom rendering logic. It primarily revolves around
OpenGL-based rendering pipelines and provides interfaces for model drawing
and rendering state initialization.
"""

from typing import Callable, Optional

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_DEPTH_TEST,
    GL_LINE_SMOOTH,
    glDisable,
    glEnable,
    glFlush,
    glLineWidth,
)
from picogl.renderer.abstract import AbstractRenderer


class RendererBase(AbstractRenderer):
    """Base Renderer Class"""

    def __init__(self, parent=None):
        """
        Initialize the renderer.

        :param state: Application state object for accessing shared data.
        """
        super().__init__()
        self.line_width = 2.0
        self.show_model = False
        self.parent = parent

    def _set_gl_state(self):
        """Set the line width and disable depth test."""
        glLineWidth(self.line_width)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)

    def _restore_gl_state(self):
        """Restore the original line width and depth test state."""
        glEnable(GL_DEPTH_TEST)

    @property
    def dispatch_list(self):
        dispatch_list: list[tuple[bool, Callable]] = [
            (self.show_model, self._draw_model),
            # Add more conditions and corresponding draw functions as needed
        ]
        return dispatch_list

    def _do_initialize(self) -> None:
        """
        Initialize OpenGL resources (shaders, atoms_buffers, etc.).
        """
        pass

    @property
    def initialized(self) -> bool:
        return self._initialized

    def render(self, mvp_matrix: Optional[np.ndarray] = None) -> None:
        """
        render dispatcher

        :return: None
        """

        for condition, draw_fn in self.dispatch_list:
            if condition:
                draw_fn()

        if hasattr(self, "_has_selection") and self._has_selection():
            self._draw_selection()

        self._finalize_render()

    def initialize_rendering_buffers(self):
        """For back compatibility"""
        self.initialize()

    def _finalize_render(self):
        """
        Finalize the rendering (e.g., flush or swap atoms_buffers).
        """
        glFlush()

    def _draw_model(self):
        """
        draw_model
        """
        raise NotImplementedError("Subclasses must implement the method.")

    def _draw_selection(self):
        """
        draw_selection
        """
        raise NotImplementedError("Subclasses must implement the method.")

    def set_visibility(self, visible: bool) -> None:
        """Set the visibility of the object."""
        pass
