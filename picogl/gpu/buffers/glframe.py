"""
This module provides classes and methods for managing OpenGL frame buffers
with functionalities for binding, clearing, and managing attachments.

The primary class, GLFramebuffer, allows creating and managing frame
buffers with support for color and depth attachments.
"""

from contextlib import contextmanager

from OpenGL.GL import (
    GL_COLOR_ATTACHMENT0,
    GL_DEPTH_ATTACHMENT,
    GL_FRAMEBUFFER,
    GL_FRAMEBUFFER_COMPLETE,
    glCheckFramebufferStatus,
    glFramebufferTexture2D,
    glGenFramebuffers,
    glGetIntegerv,
)
from OpenGL.raw.GL.VERSION.GL_3_0 import GL_FRAMEBUFFER_BINDING

from picogl.backend.gl.wrappers.frame import gl_bind_framebuffer
from picogl.renderer.initializable import Initializable
from picogl.texture.gltexture import GLTexture
from picogl.texture.texture2d import Texture2D


class GLFramebuffer(Initializable):
    """gl Framebuffer"""

    def __init__(self):
        super().__init__()
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
        self._do_initialize()

    def _do_initialize(self):
        self.handle = glGenFramebuffers(1)

    def bind(self):
        self.ensure_initialized()
        handle = self.handle
        self._bind_frame_buffer_handle(handle)

    def _bind_frame_buffer_handle(self, handle):
        gl_bind_framebuffer(GL_FRAMEBUFFER, handle)

    def unbind(self):
        """
        Unbinds any currently bound framebuffer by binding to the default framebuffer.

        This static method ensures that the OpenGL state is reset to use the default
        framebuffer, useful for concluding framebuffer operations.

        Returns:
            None
        """
        self._bind_frame_buffer_handle(0)

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
        prev = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
        self.bind()
        try:
            yield self
        finally:
            self._bind_frame_buffer_handle(prev)

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
            attachment = GL_COLOR_ATTACHMENT0 + index
            self._attach_texture(attachment, tex)
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
            self._attach_texture(GL_DEPTH_ATTACHMENT, tex)
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

    def _attach_texture(self, attachment: float | int, tex: Texture2D):
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
