from abc import ABC, abstractmethod


class AbstractRenderer(ABC):

    @abstractmethod
    def initialize(self) -> None:
        """Subclasses must implement buffer setup."""

    def set_visibility(self, visible: bool) -> None:
        """Set the visibility of the object."""
        pass

    @abstractmethod
    def render(self):
        pass

    """@abstractmethod
    def delete(self):"""
    """Release resources (VAO or equivalent)."""
