"""
Module for representing and managing OpenGL capabilities, fixed-function states, material
properties, and blend functions.

This module provides a collection of enumerations and data classes to facilitate the
representation of OpenGL states such as pipeline capabilities, blend factors, and material
properties. The module includes mappings between the defined enums and their OpenGL
integer constants for easy usage in OpenGL-related operations.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BACK, GL_BLEND, GL_BLEND_DST,
                                          GL_BLEND_SRC, GL_CULL_FACE,
                                          GL_DEPTH_TEST, GL_FRONT,
                                          GL_FRONT_AND_BACK, GL_LIGHT0,
                                          GL_LIGHT1, GL_LIGHT2, GL_LIGHT3,
                                          GL_LIGHT4, GL_LIGHTING, GL_ONE,
                                          GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA,
                                          GL_ZERO)


class GLPipelineCapability(IntEnum):
    """gl Capabilities"""

    BLEND = GL_BLEND
    DEPTH_TEST = GL_DEPTH_TEST
    CULL_FACE = GL_CULL_FACE


class GLFixedFunctionCapability(IntEnum):
    """gl Fixed Function Capabilities"""

    LIGHTING = GL_LIGHTING
    LIGHT0 = GL_LIGHT0
    LIGHT1 = GL_LIGHT1
    LIGHT2 = GL_LIGHT2
    LIGHT3 = GL_LIGHT3
    LIGHT4 = GL_LIGHT4


class GLBlendTarget(IntEnum):
    """gl Blend Dest"""

    BLEND_SRC = GL_BLEND_SRC
    BLEND_DST = GL_BLEND_DST


class GLBlendFactor(IntEnum):
    """gl Blend Factor"""

    SRC_ALPHA = GL_SRC_ALPHA
    ONE_MINUS_SRC_ALPHA = GL_ONE_MINUS_SRC_ALPHA
    ONE = GL_ONE
    ZERO = GL_ZERO

    @classmethod
    def from_gl(cls, param: int) -> "GLBlendFactor":
        try:
            return cls(param)
        except ValueError:
            raise ValueError(f"Unknown gl blend factor: {param}")

    @classmethod
    def to_gl(cls, value: "GLBlendFactor | int") -> int:
        return int(gl_value(value))


@dataclass(frozen=True)
class GLBlendFunc:
    """gl Blend Function"""

    src: GLBlendFactor
    dst: GLBlendFactor


class GLMaterialFace(IntEnum):
    """gl Material Face"""

    FRONT = GL_FRONT
    BACK = GL_BACK
    FRONT_AND_BACK = GL_FRONT_AND_BACK


@dataclass(frozen=True)
class PhongMaterial:
    """Phong Material"""

    ambient: Sequence[float] = (0.2, 0.2, 0.2, 1.0)
    diffuse: Sequence[float] = (0.8, 0.8, 0.8, 1.0)
    specular: Sequence[float] = (0.0, 0.0, 0.0, 1.0)
    shininess: float = 0.0


CAP_MAP = {
    GLPipelineCapability.BLEND: GL_BLEND,
    GLFixedFunctionCapability.LIGHTING: GL_LIGHTING,
    GLFixedFunctionCapability.LIGHT0: GL_LIGHT0,
    GLPipelineCapability.DEPTH_TEST: GL_DEPTH_TEST,
    GLPipelineCapability.CULL_FACE: GL_CULL_FACE,
}
BLEND_FACTOR_MAP = {
    GLBlendFactor.SRC_ALPHA: GL_SRC_ALPHA,
    GLBlendFactor.ONE_MINUS_SRC_ALPHA: GL_ONE_MINUS_SRC_ALPHA,
    GLBlendFactor.ONE: GL_ONE,
    GLBlendFactor.ZERO: GL_ZERO,
}
FACE_MAP = {
    GLMaterialFace.FRONT: GL_FRONT,
    GLMaterialFace.BACK: GL_BACK,
    GLMaterialFace.FRONT_AND_BACK: GL_FRONT_AND_BACK,
}
