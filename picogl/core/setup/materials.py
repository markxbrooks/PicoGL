"""
This module provides functionality to set up materials for rendering using OpenGL.

The module enables OpenGL color material functionality and applies specific material
properties to control the visual appearance of rendered objects. It utilizes Phong
shading properties such as ambient, diffuse, specular, and shininess values.
"""

from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.phong import PhongMaterial
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.core.rgbcolor import RGBAColor


def gl_setup_materials():
    """set up materials"""
    gl_enable(GLCapability.COLOR_MATERIAL)
    gl_color_material(GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE)
    # Set material properties
    material = PhongMaterial(ambient=RGBAColor.WHITE.scaled(0.2),
                             diffuse=RGBAColor.WHITE.scaled(0.8),
                             specular=RGBAColor.WHITE.with_alpha(1.0),
                             shininess=50)
    material.apply(GLMaterialFace.FRONT_AND_BACK)
