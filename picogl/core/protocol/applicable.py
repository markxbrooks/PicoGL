"""
Applicable Protocol
"""

from __future__ import annotations

from typing import Protocol, T


class Applicable(Protocol):
    def apply(self) -> None:
        ...
