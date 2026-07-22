"""
Provides functionality to set the polygon rasterization mode in OpenGL.

This module allows control over how polygons are rendered, enabling
users to render polygons as filled areas, outlines (lines), or points.
It leverages OpenGL's `glPolygonMode` for the configuration and provides
a convenient interface for its usage.
"""

from OpenGL.GL import glPolygonMode

from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.state.fill import GLFillMode


def gl_polygon_mode(face: GLMaterialFace = GLMaterialFace.FRONT_AND_BACK, mode=GLFillMode.LINE):
    """
    Sets the polygon rasterization mode for the specified face(s). This function
    specifies how polygons will be rendered by OpenGL, either as filled, lines,
    or points.

    Parameters:
    face (GLMaterialFace): Specifies the face(s) of the polygons that will be affected.
                           Can be GLMaterialFace.FRONT, GLMaterialFace.BACK, or
                           GLMaterialFace.FRONT_AND_BACK. Default is
                           GLMaterialFace.FRONT_AND_BACK.
    mode (GLFillMode): Specifies how the polygons will be rasterized. Can be
                       GLFillMode.POINT, GLFillMode.LINE, or GLFillMode.FILL.
                       Default is GLFillMode.LINE.

    """
    glPolygonMode(face, mode)
