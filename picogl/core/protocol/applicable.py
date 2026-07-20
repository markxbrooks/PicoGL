"""
Applicable Protocol
"""

from __future__ import annotations

from typing import Protocol


class Applicable(Protocol):
    def apply(self, *args) -> None:
        ...
