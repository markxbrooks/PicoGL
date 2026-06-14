from dataclasses import dataclass
from enum import Enum
from typing import Callable

from OpenGL.GL import glGetFloatv, glGetIntegerv
from OpenGL.raw.GL.ARB.viewport_array import GL_VIEWPORT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINE_WIDTH, GL_MAX_TEXTURE_SIZE
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_ACTIVE_TEXTURE
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_CURRENT_PROGRAM
from OpenGL.raw.GL.VERSION.GL_4_5 import GL_TEXTURE_BINDING_2D


@dataclass(frozen=True)
class GLParamSpec:
    """Specification for a GL state parameter."""
    pname: int
    getter: Callable
    length: int = 1


class GLParam(Enum):
    """Gl Param"""
    ACTIVE_TEXTURE = GLParamSpec(
        pname=GL_ACTIVE_TEXTURE,
        getter=glGetIntegerv,
        length=1,
    )
    TEXTURE_BINDING_2D = GLParamSpec(
        pname=GL_TEXTURE_BINDING_2D,
        getter=glGetIntegerv,
        length=1,
    )
    MAX_TEXTURE_SIZE = GLParamSpec(
        pname=GL_MAX_TEXTURE_SIZE,
        getter=glGetIntegerv,
        length=1,
    )
    VIEWPORT = GLParamSpec(
        pname=GL_VIEWPORT,
        getter=glGetIntegerv,
        length=4,
    )
    CURRENT_PROGRAM = GLParamSpec(
        pname=GL_CURRENT_PROGRAM,
        getter=glGetIntegerv,
        length=1,
    )
    LINE_WIDTH = GLParamSpec(
        pname=GL_LINE_WIDTH,
        getter=glGetFloatv,
        length=1,
    )