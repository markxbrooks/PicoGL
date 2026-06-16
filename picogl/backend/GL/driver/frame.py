from OpenGL.GL import glClear, glClearColor, glViewport

from picogl.backend.state import gl_value
from picogl.state.draw_mode import GLBitMask


class GLFrameDriver:
    """Framebuffer execution helpers for clear and viewport operations."""

    @staticmethod
    def clear(mask):
        glClear(gl_value(mask))

    def set_clear_background_and_color(self, color=(0.0, 0.0, 0.0, 1.0)):
        """
        Clears the screen to a specified color using OpenGL commands.

        This method sets the clear color and then clears the color buffer
        to ensure the screen is rendered with the specified or default background
        color.

        Args:
            color (tuple[float, float, float, float]): A tuple representing the RGBA
                color values to clear the screen. Each value should be between
                0.0 and 1.0. Defaults to (0.0, 0.0, 0.0, 1.0).
        """
        self.set_clear_color(color)
        self.clear_background()

    @staticmethod
    def set_clear_color(color=(0.0, 0.0, 0.0, 1.0)):
        glClearColor(*color)

    @staticmethod
    def viewport(x, y, width, height):
        glViewport(x, y, width, height)

    def clear_background(self):
        """
        Clears the background by removing all color and depth information from
        the current OpenGL framebuffer.

        This method clears the framebuffer's color and depth buffers, preparing
        it for rendering the next frame.

        Raises:
            OpenGL.GL.error.GLError: If an OpenGL error occurs during the
            clearing operation.
        """
        self.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
