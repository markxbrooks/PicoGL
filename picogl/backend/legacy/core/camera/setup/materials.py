"""
Setup Materials
"""

from __future__ import annotations

from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLMaterialFace, PhongMaterial
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode, GLFace
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline

# Soft Phong defaults for COLOR_MATERIAL molecule draws (near modern ambient ~0.18).
DEFAULT_SCENE_MATERIAL = PhongMaterial(
    ambient=(0.18, 0.18, 0.18, 1.0),
    diffuse=(0.8, 0.8, 0.8, 1.0),
    specular=(0.15, 0.15, 0.15, 1.0),
    shininess=32.0,
)


def setup_materials(material: PhongMaterial | None = None) -> None:
    """
    Install the default (or supplied) Phong material and enable COLOR_MATERIAL.

    Vertex colours drive ambient+diffuse; specular stays soft so colours do not
    wash out relative to modern shader shading.
    """
    mat = material if material is not None else DEFAULT_SCENE_MATERIAL
    GLLegacyPipeline.set_material(GLMaterialFace.FRONT_AND_BACK, mat)
    gl_enable(GLCapability.COLOR_MATERIAL)
    GLLegacyPipeline.set_color_material(
        GLFace.FRONT_AND_BACK,
        GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
    )
