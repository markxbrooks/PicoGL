"""
Applicable Protocol
"""

from __future__ import annotations

from typing import Protocol


class Applicable(Protocol):
    """Apply the object's current state."""

    def apply(self) -> None:
        """Apply the object's current state."""
        ...
