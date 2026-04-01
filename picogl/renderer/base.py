"""
Base Renderer Class
"""
from typing import Optional

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_DEPTH_TEST, GL_LINE_SMOOTH,
                                          glDisable, glEnable, glFlush,
                                          glLineWidth)
from picogl.renderer.abstract import AbstractRenderer


class RendererBase(AbstractRenderer):
    """Base Renderer Class"""

    def __init__(self, parent: object = None):
        """
        Initialize the renderer.

        :param state: Application state object for accessing shared data.
        """
        self.line_width = 2.0
        self.show_model = False
        self.parent = parent
        self._initialized = False

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
            (self.show_model, self._draw_model()),
            # Add more conditions and corresponding draw functions as needed
        ]
        return dispatch_list

    def initialize(self) -> None:
        """
        Initialize OpenGL resources (shaders, atoms_buffers, etc.).
        """
        if self._initialized:
            return

        self._initialized = True

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
