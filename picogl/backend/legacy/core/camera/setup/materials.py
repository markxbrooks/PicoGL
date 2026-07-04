"""
Setup Materials
"""

from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import (GLCapability, GLColorMaterialMode,
                                          GLLightParameter)
from picogl.backend.gl.wrappers.color import gl_color_material
from picogl.backend.gl.wrappers.enable import gl_enable
from picogl.backend.gl.wrappers.material import gl_material_f, gl_material_fv


def setup_materials() -> None:
    """
    setup_materials

    :return: None
    """
    gl_material_fv(
        GLMaterialFace.FRONT_AND_BACK, GLLightParameter.DIFFUSE, [1.0, 1.0, 1.0, 1.0]
    )
    gl_material_fv(
        GLMaterialFace.FRONT_AND_BACK, GLLightParameter.SPECULAR, [1.0, 1.0, 1.0, 1.0]
    )
    gl_material_f(GLMaterialFace.FRONT_AND_BACK, GLLightParameter.SHININESS, 50.0)
    gl_enable(GLCapability.COLOR_MATERIAL)
    gl_color_material(
        GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
    )
