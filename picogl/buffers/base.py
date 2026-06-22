"""
VertexBase
================

Specializes the abstract façade into a slightly more concrete base (manages a gl handle, context manager behavior, common boilerplate).

Leaves rendering-specific logic to subclasses like ModernVertexArrayGroup.

Follows the "abstract base + partial implementation" pattern.

Binding model
-------------

``bind()`` / ``unbind()`` and ``with self`` issue real gl bind/unbind on **each**
entry and exit (stack-based). This is intentionally **not** sticky/idempotent.

Do **not** inherit from :class:`~picogl.renderer.initializable.Bindable` here or on
``VertexBufferGroup`` / ``VertexArrayObject`` / per-buffer VBOs — nested ``with``
scopes and sibling buffer binds require re-binding after unbind. Pass-scoped sticky
binding belongs in small wrappers (e.g. ``ShaderPipeline``, ``LegacyClientMeshBinding``);
an optional ``StickyVAOBinding`` wrapper may be added later without changing this base.
"""

from picogl.gpu.buffers.abstract import AbstractVertexGroup
from picogl.gpu.buffers.attributes import LayoutDescriptor


class VertexBase(AbstractVertexGroup):
    """
    Generic OpenGL object interface with binding lifecycle.

    Provides handle + context manager; subclasses implement stack-based
    ``bind()`` / ``unbind()`` (not :class:`~picogl.renderer.initializable.Bindable`).
    """

    def __init__(self, handle: int = None):
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
