"""
Module providing the base class for OpenGL-managed resources.

This module includes the GLResource class, which serves as a base class
for all objects that are owned and managed by an OpenGL context. It ensures
that objects are properly associated with the OpenGL context in which
they were created and provides utility functions to validate that context.
"""

from __future__ import annotations

import sys


def _current_qt_context():
    """Return current QOpenGLContext if PySide6 is already imported; else None."""
    qtgui = sys.modules.get("PySide6.QtGui")
    if qtgui is None:
        return None
    qctx = getattr(qtgui, "QOpenGLContext", None)
    if qctx is None:
        return None
    try:
        return qctx.currentContext()
    except Exception:
        return None


class GLResource:
    """Base class for all gl-owned objects."""

    def __init__(self, handle):
        self._creation_context = _current_qt_context()
        self._deleted = False
        self._handle = handle

    @property
    def context(self):
        return self._creation_context

    def validate_context(self):
        if "PySide6.QtGui" not in sys.modules:
            return
        if self._creation_context is None:
            # Created outside a Qt context (e.g. freeglut); skip Qt checks.
            return

        ctx = _current_qt_context()

        if ctx is None:
            raise RuntimeError("No current gl context")

        if ctx is not self._creation_context:
            raise RuntimeError(
                f"Context mismatch: created in {self._creation_context}, current {ctx}"
            )
