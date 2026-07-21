"""
Phong Material
"""

from dataclasses import dataclass, field
from math import e

from picogl.backend.gl.api.material import gl_material_f, gl_material_fv
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLLightParameter
from picogl.core.data_type import rgba_tuple
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

    @classmethod
    def from_raw(
            cls,
            emission: rgba_tuple,
            ambient: rgba_tuple,
            diffuse: rgba_tuple,
            specular: rgba_tuple,
    ) -> "PhongMaterial":
        return cls(
            emission=RGBAColor(*emission),
            ambient=RGBAColor(*ambient),
            diffuse=RGBAColor(*diffuse),
            specular=RGBAColor(*specular),
        )

    def apply(
        self, face: GLMaterialFace = GLMaterialFace.FRONT_AND_BACK
    ) -> None:
        """Apply this material to a fixed-function material face."""
        gl_material_fv(face, GLLightParameter.AMBIENT, self.ambient.to_tuple())
        gl_material_fv(face, GLLightParameter.DIFFUSE, self.diffuse.to_tuple())
        gl_material_fv(face, GLLightParameter.SPECULAR, self.specular.to_tuple())
        gl_material_fv(face, GLLightParameter.EMISSION, self.emission.to_tuple())
        gl_material_f(face, GLLightParameter.SHININESS, self.shininess)
