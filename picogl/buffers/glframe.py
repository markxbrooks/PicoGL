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

from picogl.texture.gltexture import GLTexture, Texture2D


def gl_framebuffer_tex2d(tex: Texture2D):
    """
    Binds a 2D texture to the depth attachment of the currently bound framebuffer.

    This function associates a given 2D texture with the depth attachment of the
    currently active OpenGL framebuffer object. It ensures that rendering operations
    targeting the framebuffer will use the specified texture for depth buffering.

    Parameters:
        tex (Texture2D): The 2D texture to bind to the depth attachment. The `handle`
        attribute of the texture is used as a reference in this operation.
    """
    attachment=GL_DEPTH_ATTACHMENT
    gl_framebuffer_tex2d_with_attachment(attachment, tex)


def gl_framebuffer_tex2d_with_index(index: int, tex: Texture2D):
    """
    Binds a 2D texture to a specific color attachment index in the currently bound framebuffer.

    This function associates a Texture2D object with a specific color attachment point in the active
    OpenGL framebuffer. The index determines which color attachment the texture will be bound to.

    Parameters:
    index (int): The index of the color attachment in the framebuffer to which the texture is to be
    bound. The attachment point is calculated as GL_COLOR_ATTACHMENT0 + index.
    tex (Texture2D): The 2D texture object to bind to the specified color attachment.

    """
    attachment=GL_COLOR_ATTACHMENT0 + index
    gl_framebuffer_tex2d_with_attachment(attachment, tex)


def gl_framebuffer_tex2d_with_attachment(attachment: float | int, tex: Texture2D):
    """
    Binds a 2D texture to a specified framebuffer attachment point.

    This function is used to attach a 2D texture object to a specific attachment point
    of a framebuffer. The function acts as a wrapper around the OpenGL `glFramebufferTexture2D`
    to simplify the attachment process.

    Parameters:
        attachment: float | int
            The attachment point of the framebuffer to which the texture will
            be bound. This is typically an OpenGL constant value, such as
            `GL_COLOR_ATTACHMENT0`, `GL_DEPTH_ATTACHMENT`, or `GL_STENCIL_ATTACHMENT`.

        tex: Texture2D
            The texture object to be attached to the framebuffer. The texture
            must be an instance of `Texture2D` and already have an initialized
            handle.

    Raises:
        Any exception that might be triggered by the `glFramebufferTexture2D`
        function or improper argument usage.
    """
    glFramebufferTexture2D(
        target=GL_FRAMEBUFFER,
        attachment=attachment,
        textarget=GLTexture.TEXTURE_2D,
        texture=tex.handle,
        level=0,
    )


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
            gl_framebuffer_tex2d_with_index(index, tex)
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
            gl_framebuffer_tex2d(tex)
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
