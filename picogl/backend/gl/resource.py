"""
Module providing the base class for OpenGL-managed resources.

This module includes the GLResource class, which serves as a base class
for all objects that are owned and managed by an OpenGL context. It ensures
that objects are properly associated with the OpenGL context in which
they were created and provides utility functions to validate that context.
"""

from PySide6.QtGui import QOpenGLContext


class GLResource:
    """Base class for all gl-owned objects."""

    def __init__(self, handle):
        self._creation_context = QOpenGLContext.currentContext()
        self._deleted = False
        self._handle = None

    @property
    def context(self):
        return self._creation_context

    def validate_context(self):
        ctx = QOpenGLContext.currentContext()

        if ctx is None:
            raise RuntimeError("No current gl context")

        if self._creation_context is None:
            raise RuntimeError("Resource has no creation context")

        if ctx is not self._creation_context:
            raise RuntimeError(
                f"Context mismatch: created in {self._creation_context}, current {ctx}"
            )
