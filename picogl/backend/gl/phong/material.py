"""
Phong Material
"""

from dataclasses import dataclass, field

from picogl.core.rgbcolor import RGBAColor


@dataclass(frozen=True)
class PhongMaterial:
    """Phong Material"""

    ambient: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.2, 0.2, 0.2, 1.0)
    )
    diffuse: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.8, 0.8, 0.8, 1.0)
    )
    specular: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.0, 0.0, 0.0, 1.0)
    )
    emission: RGBAColor = field(
        default_factory=lambda: RGBAColor(0.0, 0.0, 0.0, 1.0)
    )
    shininess: float = 0.0
