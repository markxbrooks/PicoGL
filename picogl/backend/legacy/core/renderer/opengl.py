"""
Provides a legacy OpenGL rendering backend for handling OpenGL state changes
and material properties.

This module defines the `LegacyOpenGLBackend` class, which allows enabling
and disabling OpenGL capabilities, configuring blending functions, managing
depth masks, and setting material properties. It serves as an abstraction
over low-level OpenGL calls using the pyOpenGL library.
"""

from OpenGL.GL import glGetBooleanv
from picogl.backend.gl.state.fill import GLLightParameter
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_DEPTH_WRITEMASK,
    glDepthMask,
    glBlendFunc,
    glDisable,
    glEnable,
    glIsEnabled,
    glMaterialf,
    glMaterialfv,
)
from picogl.backend.gl.capability import FACE_MAP, GLMaterialFace, PhongMaterial
from picogl.renderer.backend import RenderBackend
from picogl.boolean import GLBoolean


def gl_enable(self, cap):
    glEnable(cap)
    
    
def gl_disable(self, cap):
    glDisable(cap)
    
    
def gl_is_enabled(self, cap):
    return glIsEnabled(cap)
    

def gl_blend_func(self, src, dst):
    glBlendFunc(src, dst)
    

def gl_set_depth_mask(self, flag):
    glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)
        

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
        glDepthMask(GLBoolean.TRUE if flag else GLBoolean.FALSE)

    def get_depth_mask(self):
        return glGetBooleanv(GL_DEPTH_WRITEMASK)

    def set_material(self, face: GLMaterialFace, mat: PhongMaterial):
        f = FACE_MAP[face]

        glMaterialfv(f, GLLightParameter.AMBIENT, mat.ambient)
        glMaterialfv(f, GLLightParameter.DIFFUSE, mat.diffuse)
        glMaterialfv(f, GLLightParameter.SPECULAR, mat.specular)
        glMaterialf(f, GLLightParameter.SHININESS, mat.shininess)
