"""Default chain coloring for molecular meshes."""

from __future__ import annotations

from picogl.core.rgbcolor import RGBColor

_CHAIN_RGB = {
    "A": RGBColor.GREEN.to_tuple(),
    "B": RGBColor.BLUE.to_tuple(),
}


def chain_rgb(chain_id: str) -> tuple[float, float, float]:
    """Return an RGB tuple for a PDB chain identifier."""
    return _CHAIN_RGB.get(chain_id, RGBColor.WHITE.to_tuple())
