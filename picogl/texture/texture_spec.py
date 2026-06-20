"""
TextureSpec
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class TextureSpec:
    """Texture Spec"""

    width: int
    height: int
    format: str = "rgb"
    min_filter: str = "linear"
    mag_filter: str = "linear"
    wrap_s: str = "clamp"
    wrap_t: str = "clamp"

