"""
Helpers for normalizing OpenGL integer query results.
"""

from __future__ import annotations

from typing import Any


def as_gl_int(value: Any) -> int:
    """Normalize ``glGet*`` results (scalar or length-1 array) to ``int``."""
    if hasattr(value, "__len__") and not isinstance(value, (bytes, str)):
        return int(value[0])
    return int(value)
