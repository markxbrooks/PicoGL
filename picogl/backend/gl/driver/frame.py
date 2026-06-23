"""
A module providing helper operations for framebuffer execution,
including clearing framebuffer and setting viewport.

This module utilizes OpenGL commands to perform operations like clearing
the framebuffer with specified colors and configuring the viewport
for rendering.
"""

from OpenGL.GL import glViewport
from OpenGL.GL import GL_FRAMEBUFFER, glBindFramebuffer

from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.wrappers.clear import gl_clear_color, gl_clear
from picogl.backend.state import gl_value


class GLFrameDriver:
    """Framebuffer execution helpers for clear and viewport operations."""

    @staticmethod
    def clear(mask):
        gl_clear(gl_value(mask))

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
    def bind_framebuffer(framebuffer: int) -> None:
        """Bind the window-system default framebuffer (required on some Qt/macOS paths)."""
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    def bind_default_framebuffer(self) -> None:
        """Bind the window-system default framebuffer (required on some Qt/macOS paths)."""
        self.bind_framebuffer(framebuffer=0)

    def set_clear_color_only(
            self, color: tuple[float, float, float, float]
    ) -> None:
        """Set the clear color without clearing (safe before the default FBO is ready)."""
        self.bind_default_framebuffer()
        self.set_clear_color(color)

    @staticmethod
    def set_clear_color(color=(0.0, 0.0, 0.0, 1.0)):
        gl_clear_color(color)

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
            OpenGL.gl.error.GLError: If an OpenGL error occurs during the
            clearing operation.
        """
        self.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
