"""
Provides functions to set material properties for geometry objects in OpenGL.

This module facilitates interaction with the OpenGL rendering pipeline by
allowing the configuration of material parameters for different faces of
geometry objects. It exposes functions for setting material properties
using single-floating point values or sequences of floating-point values.
"""

from typing import Any, Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import glMaterialf, glMaterialfv

from picogl.backend.gl.state.fill import GLLightParameter


def gl_material_fv(face: Any, pname: GLLightParameter, param: Sequence[float]):
    """
    Sets material properties for a specified face of a geometry object.

    This function is used to define material properties for rendering using the
    OpenGL pipeline. It assigns material parameters to either the front, back,
    or both faces of an object in the current OpenGL context.

    Parameters:
        face (Any): Specifies which face or faces will be updated.
            Possible values are GL_FRONT, GL_BACK, or GL_FRONT_AND_BACK.
        pname (GLLightParameter): The symbolic name of a material parameter
            to be set. For example, GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR,
            GL_EMISSION, or GL_SHININESS.
        param (Sequence[float]): Specifies the values for the material
            parameter indicated by pname. It should be a sequence of one
            or multiple floating-point numbers, depending on pname.
    """
    glMaterialfv(face, pname, param)


def gl_material_f(face: Any, pname: GLLightParameter, param: float):
    """
    Sets the material property for a specified face of a graphical object in OpenGL.

    This function calls the OpenGL `glMaterialf` function to set a single material
    property for a given face with a specified parameter value.

    Parameters:
    face : Any
        Specifies which face or faces are being updated.
        Acceptable values typically include OpenGL constants like `GL_FRONT`,
        `GL_BACK`, or `GL_FRONT_AND_BACK`.
    pname : GLLightParameter
        Specifies the material parameter to be updated. Must be an OpenGL enum
        constant that corresponds to a material property, such as `GL_AMBIENT`,
        `GL_DIFFUSE`, or `GL_SPECULAR`.
    param : float
        Specifies the value for the material property being updated.

    """
    glMaterialf(face, pname, param)
