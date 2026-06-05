from dataclasses import dataclass
from typing import Sequence

from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_BACK, GL_BLEND, GL_CULL_FACE,
                                          GL_DEPTH_TEST, GL_FRONT,
                                          GL_FRONT_AND_BACK, GL_LIGHT0,
                                          GL_LIGHTING, GL_ONE,
                                          GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA,
                                          GL_ZERO)
from picogl.utils.strenum import StrEnum


class GLPipelineCapability(StrEnum):
    """GL Capabilities"""
    BLEND = "blend"
    DEPTH_TEST = "depth_test"
    CULL_FACE = "cull_face"


class GLStateValue(StrEnum):
    """GL State Value"""
    DEPTH_MASK = "depth_mask"


class GLFixedFunctionCapability(StrEnum):
    """GL Fixed Function Capabilities"""
    LIGHTING = "lighting"
    LIGHT0 = "light0"


class GLBlendFactor(StrEnum):
    """GL BLend Factor"""
    SRC_ALPHA = "src_alpha"
    ONE_MINUS_SRC_ALPHA = "one_minus_src_alpha"
    ONE = "one"
    ZERO = "zero"


@dataclass(frozen=True)
class GLBlendFunc:
    """GL Blend Function"""
    src: GLBlendFactor
    dst: GLBlendFactor


class GLMaterialFace(StrEnum):
    """GL Material Face"""
    FRONT = "front"
    BACK = "back"
    FRONT_AND_BACK = "front_and_back"


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