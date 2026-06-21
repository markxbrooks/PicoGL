def current_gl_context() -> int:
    try:
        from PySide6.QtGui import QOpenGLContext

        # return QOpenGLContext.currentContext()
        return id(QOpenGLContext.currentContext())
    except Exception:
        return None
