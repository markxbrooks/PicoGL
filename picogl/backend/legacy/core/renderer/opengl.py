"""
Provides a legacy OpenGL rendering backend for handling OpenGL state changes
and material properties.

This module defines the `LegacyOpenGLBackend` class, which allows enabling
and disabling OpenGL capabilities, configuring blending functions, managing
depth masks, and setting material properties. It serves as an abstraction
over low-level OpenGL calls using the pyOpenGL library.
"""

from OpenGL.GL import glGetBooleanv
from OpenGL.raw.GL.VERSION.GL_1_0 import glEnable, glDisable, glIsEnabled, glBlendFunc, GL_DEPTH_WRITEMASK, \
    glMaterialfv, GL_AMBIENT, GL_DIFFUSE, GL_SPECULAR, glMaterialf, GL_SHININESS

from picogl.backend.capability import GLMaterialFace, PhongMaterial, FACE_MAP
from picogl.renderer.backend import RenderBackend


class LegacyOpenGLBackend(RenderBackend):
    """Legacy OpenGL Backend"""
    def enable(self, cap): glEnable(cap)
    def disable(self, cap): glDisable(cap)
    def is_enabled(self, cap): return glIsEnabled(cap)

    def set_blend_func(self, src, dst):
        glBlendFunc(src, dst)

    def set_depth_mask(self, flag):
        from OpenGL.GL import glDepthMask, GL_TRUE, GL_FALSE
        glDepthMask(GL_TRUE if flag else GL_FALSE)

    def get_depth_mask(self):
        return glGetBooleanv(GL_DEPTH_WRITEMASK)

    def set_material(self, face: GLMaterialFace, mat: PhongMaterial):
        f = FACE_MAP[face]

        glMaterialfv(f, GL_AMBIENT, mat.ambient)
        glMaterialfv(f, GL_DIFFUSE, mat.diffuse)
        glMaterialfv(f, GL_SPECULAR, mat.specular)
        glMaterialf(f, GL_SHININESS, mat.shininess)
