import sys

from OpenGL import GL as gl
from picogl.ui.abc_window import AbstractGLWindow


class GLWindow(AbstractGLWindow):
    """GLWindow"""

    def initializeGL(self) -> None:
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl_enable(gl.GL_DEPTH_TEST)

    def paintGL(self) -> None:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # ... render your scene ...

    def resizeGL(self, w: int, h: int) -> None:
        self.width, self.height = w, h
        gl.glViewport(0, 0, w, h)
        # If you use a projection matrix, update it here
        # GLU.gluPerspective(...)

    def keyPressEvent(self, key, x, y) -> None:
        if key == b"\x1b":  # Escape
            sys.exit(0)

    def on_special_key(self, key, x, y) -> None:
        pass

    def mousePressEvent(self, button, state, x, y) -> None:
        pass

    def mouseMoveEvent(self, x, y) -> None:
        pass


if __name__ == "__main__":
    win = GLWindow()
    win.run()
