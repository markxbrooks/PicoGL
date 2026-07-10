"""
Provides a legacy OpenGL rendering backend for handling OpenGL state changes
and material properties.

This module defines the `LegacyOpenGLBackend` class, which allows enabling
and disabling OpenGL capabilities, configuring blending functions, managing
depth masks, and setting material properties. It serves as an abstraction
over low-level OpenGL calls using the pyOpenGL library.
"""

from picogl.backend.gl.api.blending import gl_blend_func
from picogl.backend.gl.api.depth import gl_get_depth_mask, gl_set_depth_mask
from picogl.backend.gl.api.enable import gl_disable, gl_enable, gl_is_enabled
from picogl.backend.gl.api.material import gl_material_f, gl_material_fv
from picogl.backend.gl.capability import FACE_MAP, GLMaterialFace, PhongMaterial
from picogl.backend.gl.state.fill import GLLightParameter
from picogl.renderer.backend import RenderBackend


class LegacyOpenGLBackend(RenderBackend):
    """Legacy OpenGL Backend"""

    def enable(self, cap):
        gl_enable(cap)

    def disable(self, cap):
        gl_disable(cap)

    def is_enabled(self, cap):
        return gl_is_enabled(cap)

    def set_blend_func(self, src, dst):
        gl_blend_func(src, dst)

    def set_depth_mask(self, flag):
        gl_set_depth_mask(flag)

    def get_depth_mask(self):
        return gl_get_depth_mask()

    def set_material(self, face: GLMaterialFace, mat: PhongMaterial):
        f = FACE_MAP[face]

        gl_material_fv(f, GLLightParameter.AMBIENT, mat.ambient)
        gl_material_fv(f, GLLightParameter.DIFFUSE, mat.diffuse)
        gl_material_fv(f, GLLightParameter.SPECULAR, mat.specular)
        gl_material_f(f, GLLightParameter.SHININESS, mat.shininess)
