"""
A module for controlling OpenGL material properties and color settings.

This module provides convenient access to OpenGL functions for setting material
properties and color attributes when working with the OpenGL rendering pipeline.
It includes utilities to specify how material faces interact with colors and
how color values are applied in the rendering process.

Functions:
- gl_color_material: Configures material properties for specific faces in the
  OpenGL lighting model.
- gl_color_3f: Sets the color values using RGB components.
"""

from OpenGL.GL import glColorMaterial
from OpenGL.raw.GL.VERSION.GL_1_0 import glColor3f, glColor4f
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLColorMaterialMode
from picogl.core.rgbcolor import RGBColor


def gl_color_material(face: GLMaterialFace, mode: GLColorMaterialMode) -> None:
    """
    Sets the material properties for the specified face and mode in the OpenGL rendering state.

    This function is a wrapper around the OpenGL `glColorMaterial` functionality,
    which allows specifying how material color properties are assigned when using
    coloring operations. It adjusts the behavior of color tracking for the OpenGL
    lighting model on specific material faces to improve rendering flexibility.

    Parameters:
    face: GLMaterialFace
        Specifies the material face to be updated. Valid options include constants
        such as `GL_FRONT`, `GL_BACK`, or `GL_FRONT_AND_BACK`.
    mode: GLColorMaterialMode
        Defines the material property for which the color is to be applied. Valid
        values can include `GL_AMBIENT`, `GL_DIFFUSE`, `GL_SPECULAR`, `GL_AMBIENT_AND_DIFFUSE`,
        or other accepted OpenGL material property constants.
    """
    glColorMaterial(face, mode)


def gl_color_rgb(rgb_color: RGBColor) -> None:
    """
    Sets the current OpenGL color using the RGB values provided.

    The function takes a color represented as a tuple of three float values
    in the range [0.0, 1.0] corresponding to the red, green, and blue components
    and applies it using the OpenGL `glColor3f` function.

    Args:
        rgb_color (tuple[float, float, float]): RGB obect containing the red, green,
                                            and blue components of the color.

    Returns:
        None
    """
    glColor3f(*rgb_color.to_tuple())


def gl_color_4f(color: tuple[float, float, float, float]) -> None:
    glColor4f(*color)


def gl_color_3f(color: tuple[float, float, float]) -> None:
    """
    Sets the current OpenGL color using the RGB values provided.

    The function takes a color represented as a tuple of three float values
    in the range [0.0, 1.0] corresponding to the red, green, and blue components
    and applies it using the OpenGL `glColor3f` function.

    Args:
        color (tuple[float, float, float]): A tuple containing the red, green,
                                            and blue components of the color.

    Returns:
        None
    """
    glColor3f(*color)
