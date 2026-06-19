"""
VertexBase
================

Specializes the abstract façade into a slightly more concrete base (manages a GL handle, context manager behavior, common boilerplate).

Leaves rendering-specific logic to subclasses like ModernVertexArrayGroup.

Follows the "abstract base + partial implementation" pattern.
"""

from picogl.buffers.abstract import AbstractVertexGroup
from picogl.buffers.attributes import LayoutDescriptor


class VertexBase(AbstractVertexGroup):
    """
    Generic OpenGL object interface with binding lifecycle.

    Provides handle + context manager, leaves binding to subclasses.
    """

    def __init__(self, handle: int = None):
        super().__init__()
        self.handle = handle

    def bind(self):
        raise NotImplementedError

    def unbind(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        """Attach the buffers that the VAO/group should coordinate."""
        pass

    def set_layout(self, layout: LayoutDescriptor) -> None:
        """Define the attribute layout for this VAO/group."""
        pass
