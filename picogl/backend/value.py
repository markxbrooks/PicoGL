"""
Render-state descriptors and command helpers for PicoGL backends.

The classes in this module are intentionally backend-neutral: they describe
desired OpenGL state and delegate the actual gl calls to a backend object.
"""
from enum import Enum
from typing import Any


from picogl.backend.gl.capability import (
    BLEND_FACTOR_MAP,
    CAP_MAP,
    FACE_MAP,

)


def gl_value(value: Any) -> Any:
    """Return a raw OpenGL value for PicoGL enums or pass raw values through."""
    for mapping in (CAP_MAP, BLEND_FACTOR_MAP, FACE_MAP):
        try:
            if value in mapping:
                return mapping[value]
        except TypeError:
            pass

    enum_value = getattr(value, "value", value)
    if isinstance(value, Enum):
        return enum_value
    return value

