"""OpenGL context checks for shader compile/bind (Qt + headless)."""

from __future__ import annotations

from OpenGL import GL as gl


def clear_gl_errors(max_clear: int = 8) -> None:
    """Drain pending GL errors so the next call's status is meaningful."""
    for _ in range(max_clear):
        err = gl.glGetError()
        if err == gl.GL_NO_ERROR:
            return


def gl_context_available() -> bool:
    """True when a GL context is current and ``glGetString(GL_VERSION)`` works."""
    try:
        from PySide6.QtGui import QOpenGLContext

        ctx = QOpenGLContext.currentContext()
        if ctx is not None and ctx.isValid():
            return True
    except Exception:
        pass
    try:
        return gl.glGetString(gl.GL_VERSION) is not None
    except Exception:
        return False


def require_gl_context(operation: str) -> None:
    if not gl_context_available():
        raise RuntimeError(
            f"{operation} requires a current OpenGL context "
            "(call from initializeGL / paintGL with the widget context current)"
        )


def program_is_valid(program_id: int | None) -> bool:
    if program_id is None:
        return False
    try:
        return bool(gl.glIsProgram(int(program_id)))
    except Exception:
        return False
