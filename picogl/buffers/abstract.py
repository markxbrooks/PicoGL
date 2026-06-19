"""
Abstract render atoms_buffers class
"""

from abc import ABC, abstractmethod

from picogl.buffers.attributes import LayoutDescriptor
from picogl.renderer.initializable import Bindable


class AbstractVertexGroup(Bindable, ABC):
    """Public façade"""

    @abstractmethod
    def bind(self) -> None:
        """Bind the underlying VAO/state for rendering."""
        pass

    @abstractmethod
    def unbind(self) -> None:
        """Optionally unbind the VAO/state."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Release resources (VAO or equivalent)."""
        pass

    @abstractmethod
    def set_layout(self, layout: LayoutDescriptor) -> None:
        """Define the attribute layout for this VAO/group."""
        pass

    @abstractmethod
    def attach_buffers(self, nbo=None, cbo=None, vbo=None, ebo=None) -> None:
        """Attach the buffers that the VAO/group should coordinate."""
        pass
