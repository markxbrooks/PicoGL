from abc import ABC, abstractmethod

from picogl.renderer.initializable import Initializable


class AbstractRenderer(Initializable, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _do_initialize(self) -> None:
        """Subclasses must implement actual setup."""

    def set_visibility(self, visible: bool) -> None:
        """Set the visibility of the object."""
        pass

    @abstractmethod
    def render(self):
        pass

    """@abstractmethod
    def delete(self):"""
    """Release resources (VAO or equivalent)."""
