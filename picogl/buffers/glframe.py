"""
This module provides classes and methods for managing OpenGL frame buffers
with functionalities for binding, clearing, and managing attachments.

The primary class, GLFramebuffer, allows creating and managing frame
buffers with support for color and depth attachments.
"""
from OpenGL.GL import (GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, glClear,
                                          glClearColor)


class GLFramebuffer:
    """GL Frame Buffer"""

    def __init__(self):
        self.color_attachments = []
        self.depth_attachment = None

    def bind(self):
        """bind"""
        pass

    def clear(self, color=(0.0, 0.0, 0.0, 1.0)):
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
        glClearColor(*color)
        self.clear_background()

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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
