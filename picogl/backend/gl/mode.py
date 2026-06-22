"""
gl Mode
"""

from enum import Enum


# class GlMode(str):
class GLMode(str, Enum):
    """OpenGL rendering mode"""

    LEGACY = "legacy"
    MODERN = "modern"

    @classmethod
    def choices(cls):
        return [m.value for m in cls]
