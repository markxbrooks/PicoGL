"""
Glut Window
"""

import sys

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

# Must run before OpenGL.GLUT: Homebrew freeglut shadows Apple GLUT on macOS.
import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from OpenGL import platform as gl_platform
from picogl.backend.legacy.core.camera.projection_state import GLUProjectionState
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.state import GLViewport
from picogl.core.camera import ProjectionConfig
from picogl.ui.abc_window import AbstractGLWindow


class GLWindow(AbstractGLWindow):
    """GLWindow"""

    # Default zoom camera state (also mirrored onto ``self.context`` when present).
    DEFAULT_ZOOM_FOV: float = float(ProjectionConfig.fovy)
    DEFAULT_ZOOM_DISTANCE: float = 10.0
    DEFAULT_DISTANCE_THRESHOLD: float = 5.0

    def __init__(self, title: str = "window", *args, **kwargs):
        """__init__"""
        super().__init__()
        self.window = None
        self.viewport = GLViewport()
        self.projection_config = ProjectionConfig()
        self.projection = GLUProjectionState()
        # Optional initial size (used by glutInitWindowSize before subclasses run).
        self.width = kwargs.pop("width", None)
        self.height = kwargs.pop("height", None)
        self.title = title
        # Zoom state used by wheelEvent; subclasses may override defaults.
        self.zoom_fov: float = self.DEFAULT_ZOOM_FOV
        self.zoom_distance: float = self.DEFAULT_ZOOM_DISTANCE
        self.distance_threshold: float = self.DEFAULT_DISTANCE_THRESHOLD
        self.context = None
        self.init_glut()
        self.controller = None
        self.update_if = GLUT.glutPostRedisplay
        self.sync_zoom_to_context()

    def sync_zoom_to_context(self) -> None:
        """Copy window zoom fields onto ``self.context`` when it exists."""
        ctx = getattr(self, "context", None)
        if ctx is None:
            return
        ctx.zoom_fov = self.zoom_fov
        ctx.zoom_distance = self.zoom_distance
        ctx.distance_threshold = self.distance_threshold

    def wheelEvent(self, wheel=0, direction=0, x=0, y=0):
        """
        Mouse wheel zoom: adjusts distance if far, FOV if close.
        Positive direction -> zoom in, Negative -> zoom out.
        """
        zoom_step = direction * 0.5

        if self.zoom_distance > self.distance_threshold:
            # Distance zoom
            self.zoom_distance = max(1.0, self.zoom_distance - zoom_step)
        else:
            # FOV zoom
            self.zoom_fov = max(10.0, min(90.0, self.zoom_fov - zoom_step))
        self.sync_zoom_to_context()
        print(
            f"Zoom mode: {'distance' if self.zoom_distance > self.distance_threshold else 'fov'} "
            f"| Distance: {self.zoom_distance:.2f} | FOV: {self.zoom_fov:.2f}"
        )
        self.update_mvp()

    def update_mvp(self) -> None:
        """Refresh MVP from current zoom/viewport and request a redraw.

        Subclasses with a richer camera (e.g. GlutRendererWindow) should
        override this. Default path calls ``calculate_mvp`` when present.
        """
        self.sync_zoom_to_context()
        width = self.width or getattr(self.viewport, "width", None) or 800
        height = self.height or getattr(self.viewport, "height", None) or 480
        calculate = getattr(self, "calculate_mvp", None) or getattr(
            self, "calculate_mvp_matrix", None
        )
        if callable(calculate):
            calculate(width, height)
        self.update()

    def init_glut(self):
        """init_glut"""
        GLUT.glutInit(sys.argv)
        GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
        # Prefer the size set by subclasses (e.g. GlutRendererWindow); fall back to 800x480.
        init_w = getattr(self, "width", None) or 800
        init_h = getattr(self, "height", None) or 480
        GLUT.glutInitWindowSize(int(init_w), int(init_h))
        if self.title is not None:
            title_bytes = self.title.encode("utf-8")
        else:
            title_bytes = b"Window Title"
        self.window = GLUT.glutCreateWindow(title_bytes)
        if not gl_platform.GetCurrentContext():
            glut_lib = getattr(getattr(GLUT, "platform", None), "PLATFORM", None)
            glut_name = getattr(getattr(glut_lib, "GLUT", None), "_name", "unknown")
            raise RuntimeError(
                "GLUT window created but no OpenGL context is current "
                f"(GLUT library: {glut_name}). On macOS, Homebrew freeglut "
                "(X11/Mesa) often shadows Apple GLUT.framework — ensure "
                "picogl.ui.backend.glut.prefer_apple_glut loads first, or use "
                "the Qt examples (e.g. picogl/examples/qt_cube_simple.py)."
            )
        GLUT.glutDisplayFunc(self.display)
        GLUT.glutReshapeFunc(self.resizeGL)
        GLUT.glutKeyboardFunc(self.keyPressEvent)
        GLUT.glutSpecialFunc(self.on_special_key)
        GLUT.glutMouseFunc(self.mousePressEvent)
        GLUT.glutMotionFunc(self.mouseMoveEvent)
        # freeglut extension; absent from Apple GLUT.framework
        glut_lib = GLUT.platform.PLATFORM.GLUT
        if hasattr(glut_lib, "glutMouseWheelFunc"):
            GLUT.glutMouseWheelFunc(self.wheelEvent)

    def initializeGL(self):
        """initialize_gl"""
        gl_initialize_background()

    def paintGL(self):
        """paintGL"""
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GLU.gluLookAt(4.0, 3.0, -3.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        # built in model_matrix
        GLUT.glutSolidTeapot(1)
        print("please override paintGL")

    def update(self):
        """draw"""
        GLUT.glutPostRedisplay()

    def display(self):
        """display"""
        self.paintGL()
        GLUT.glutSwapBuffers()

    def idle(self):
        """idle"""
        pass

    def resizeGL(self, width: int, height: int):
        """resize"""
        print("please override resize")
        self.viewport.width = width
        self.viewport.height = height
        self.width = width
        self.height = height
        self.viewport.apply()
        aspect = float(width) / float(max(height, 1))
        self.projection.apply(self.projection_config.with_aspect(aspect))

    def keyPressEvent(self, key, x, y):
        """on_keyboard"""
        if self.controller is not None:
            self.controller.on_keyboard(key, x, y)
        else:
            print("please overrider on_keyboard")

    def on_special_key(self, key, x, y):
        """on_special_key"""
        if self.controller is not None:
            self.controller.on_special_key(key, x, y)
        else:
            print("please overrider on_keyboard")

    def mousePressEvent(self, *args, **kwargs):
        """on_mouse"""
        if self.controller is not None:
            self.controller.mousePressEvent(*args, **kwargs)
        else:
            print("please overrider on_mouse")

    def mouseMoveEvent(self, *args, **kwargs):
        """on_mousemove"""
        if self.controller is not None:
            self.controller.mouseMoveEvent(*args, **kwargs)
        else:
            print("please overrider on_mousemove")

    def run(self):
        """run"""
        GLUT.glutMainLoop()


if __name__ == "__main__":
    win = GLWindow()
    win.run()
