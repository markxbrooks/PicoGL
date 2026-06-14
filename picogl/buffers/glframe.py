"""
This module provides classes and methods for managing OpenGL frame buffers
with functionalities for binding, clearing, and managing attachments.

The primary class, GLFramebuffer, allows creating and managing frame
buffers with support for color and depth attachments.
"""
from contextlib import contextmanager

from OpenGL.GL import (glBindFramebuffer, GL_FRAMEBUFFER, glFramebufferTexture2D,
                       GL_COLOR_ATTACHMENT0, glCheckFramebufferStatus, GL_FRAMEBUFFER_COMPLETE,
                       glGenFramebuffers, GL_DEPTH_ATTACHMENT)

from picogl.texture.gltexture import GLTexture


class GLFramebuffer:
    """GL Framebuffer"""

    def __init__(self):
        self.handle = None
        self.color_attachments: list[int] = []
        self.depth_attachment: int | None = None

    def initialize(self):
        """
        Initializes the framebuffer object.

        Generates and assigns a new framebuffer handle if one does not already
        exist. This method is used to allocate OpenGL resources for rendering
        operations involving a framebuffer.

        Raises:
            RuntimeError: If there is an issue generating a new framebuffer.

        """
        if self.handle is not None:
            return
        self.handle = glGenFramebuffers(1)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.handle)

    @staticmethod
    def unbind():
        """
        Unbinds any currently bound framebuffer by binding to the default framebuffer.

        This static method ensures that the OpenGL state is reset to use the default
        framebuffer, useful for concluding framebuffer operations.

        Returns:
            None
        """
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    @contextmanager
    def bound(self):
        """
        Context manager to handle the binding and unbinding of a GLFramebuffer.

        This context manager ensures that when a GLFramebuffer is bound, it is properly
        unbound after the block of code within the context completes, even if an
        exception is raised.

        Yields:
            GLFramebuffer: The GLFramebuffer instance being managed.
        """
        self.bind()
        try:
            yield self
        finally:
            GLFramebuffer.unbind()

    def attach_color_texture(self, tex: "Texture2D", index: int = 0):
        """
        Attaches a color texture to the framebuffer at a specified index.

        This method binds a 2D texture to a color attachment point of the framebuffer.
        The `index` parameter specifies the color attachment index to which the texture
        will be attached. The method also keeps track of texture handles attached
        to the framebuffer's color attachments.

        Parameters:
            tex (Texture2D): The 2D texture to attach to the framebuffer.
            index (int): The color attachment index. Defaults to 0.

        Returns:
            None
        """
        with self.bound():
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0 + index,
                GLTexture.TEXTURE_2D,
                tex.handle,
                0,
            )
            self.color_attachments.append(tex.handle)

    def attach_depth_texture(self, tex: "Texture2D"):
        """
        Attaches a texture as the depth attachment to the framebuffer.

        This method binds the framebuffer and attaches the given 2D texture to the
        depth attachment point. It updates the depth attachment handle.

        Parameters:
            tex (Texture2D): The texture to attach as the depth attachment.

        """
        with self.bound():
            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                GLTexture.TEXTURE_2D,
                tex.handle,
                0,
            )
            self.depth_attachment = tex.handle

    def check_complete(self):
        """
        Checks the completeness of the currently bound framebuffer.

        This method verifies the status of the currently bound OpenGL framebuffer
        by using the `glCheckFramebufferStatus` function. If the framebuffer is
        not complete, it raises a `RuntimeError` with the corresponding status
        code.

        Raises:
            RuntimeError: If the framebuffer is not complete, with the status code
            indicating the specific issue.
        """
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Incomplete framebuffer: {status}")
