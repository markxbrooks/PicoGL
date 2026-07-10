"""
A module providing helper operations for framebuffer execution,
including clearing framebuffer and setting viewport.

This module utilizes OpenGL commands to perform operations like clearing
the framebuffer with specified colors and configuring the viewport
for rendering.
"""

from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy.scale import gl_viewport
from picogl.backend.gl.api.clear import gl_clear, gl_clear_color
from picogl.backend.gl.api.frame import gl_bind_framebuffer
from picogl.backend.state import gl_value
from picogl.core.rgbcolor import RGBAColor, clamp01

from elmo.ui.widgets.gl.mol.viewport import Viewport


class GLFrameDriver:
    """Framebuffer execution helpers for clear and viewport operations."""

    def __init__(self):
        self.viewport: Viewport = Viewport(0, 0, 0, 0)

    @staticmethod
    def clear(mask):
        gl_clear(gl_value(mask))

    def set_clear_background_and_color_from_rgba(
        self, color: RGBAColor = RGBAColor(0.0, 0.0, 0.0, 1.0)
    ) -> None:
        """
        Clears the screen to a specified color using OpenGL commands.

        Args:
            color (RGBA): color values to clear the screen. Each component is clamped to [0.0, 1.0].
        """
        color = RGBAColor(
            clamp01(color.r),
            clamp01(color.g),
            clamp01(color.b),
            clamp01(color.a),
        )
        rgba = to_rgba_tuple(color)
        self.set_clear_color(rgba.to_tuple())

        self.clear_background()

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
        gl_bind_framebuffer(framebuffer)

    def bind_default_framebuffer(self) -> None:
        """Bind the window-system default framebuffer (required on some Qt/macOS paths)."""
        self.bind_framebuffer(framebuffer=0)

    def set_clear_color_only(self, color: tuple[float, float, float, float]) -> None:
        """Set the clear color without clearing (safe before the default FBO is ready)."""
        self.bind_default_framebuffer()
        self.set_clear_color(color)

    @staticmethod
    def set_clear_color(color=(0.0, 0.0, 0.0, 1.0)):
        gl_clear_color(color)

    def set_viewport(self, viewport: Viewport):
        self.viewport = viewport
        gl_viewport(viewport.x, viewport.y, viewport.width, viewport.height)

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
