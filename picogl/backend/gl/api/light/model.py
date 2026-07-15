from __future__ import annotations

from OpenGL.raw.GL.VERSION.GL_1_0 import glLightModelfv


def gl_light_model_fv(pname, params):
    """gl_light_model_fv"""
    glLightModelfv(pname, params)
