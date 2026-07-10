"""
Material
"""

from typing import Any, Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import glMaterialf, glMaterialfv
from picogl.backend.gl.state.fill import GLLightParameter


def gl_material_fv(face: Any, pname: GLLightParameter, param: Sequence[float]):
    glMaterialfv(face, pname, param)


def gl_material_f(face: Any, pname: GLLightParameter, param: float):
    glMaterialf(face, pname, param)
