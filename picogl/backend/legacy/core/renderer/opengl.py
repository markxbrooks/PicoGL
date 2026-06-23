"""
Provides a legacy OpenGL rendering backend for handling OpenGL state changes
and material properties.

This module defines the `LegacyOpenGLBackend` class, which allows enabling
and disabling OpenGL capabilities, configuring blending functions, managing
depth masks, and setting material properties. It serves as an abstraction
over low-level OpenGL calls using the pyOpenGL library.
"""

from OpenGL.GL import glGetBooleanv
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_AMBIENT,
    GL_DEPTH_WRITEMASK,
    GL_DIFFUSE,
    GL_SHININESS,
    GL_SPECULAR,
    glBlendFunc,
    glDisable,
    glEnable,
    glIsEnabled,
    glMaterialf,
    glMaterialfv,
)
from picogl.backend.gl.capability import FACE_MAP, GLMaterialFace, PhongMaterial
from picogl.renderer.backend import RenderBackend


class LegacyOpenGLBackend(RenderBackend):
    """Legacy OpenGL Backend"""

    def enable(self, cap):
        glEnable(cap)

    def disable(self, cap):
        glDisable(cap)

    def is_enabled(self, cap):
        return glIsEnabled(cap)

    def set_blend_func(self, src, dst):
        glBlendFunc(src, dst)

    def set_depth_mask(self, flag):
        from OpenGL.GL import GL_FALSE, GL_TRUE, glDepthMask

        glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)

    def get_depth_mask(self):
        return glGetBooleanv(GL_DEPTH_WRITEMASK)

    def set_material(self, face: GLMaterialFace, mat: PhongMaterial):
        f = FACE_MAP[face]

        glMaterialfv(f, GLLightParameter.AMBIENT, mat.ambient)
        glMaterialfv(f, GLLightParameter.DIFFUSE, mat.diffuse)
        glMaterialfv(f, GLLightParameter.SPECULAR, mat.specular)
        glMaterialf(f, GLLightParameter.SHININESS, mat.shininess)
