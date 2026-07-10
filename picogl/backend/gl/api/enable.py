"""
gl enable disable is enabled
"""

from typing import Union

from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled
from picogl.backend.gl.capability import GLFixedFunctionCapability, GLPipelineCapability
from picogl.backend.gl.enums.legacy import GLLegacyClipPlane
from picogl.backend.gl.enums.point_size import (
    GLLegacyPointCapability,
    GLPointCapability,
)
from picogl.backend.gl.state.fill import GLCapability

GLCapabilities = Union[
    GLCapability,
    GLLegacyPointCapability,
    GLPointCapability,
    GLFixedFunctionCapability,
    GLPipelineCapability,
    GLLegacyClipPlane,
]


def gl_enable(
    cap: GLCapabilities,
):
    """enable gl_enable capability"""
    glEnable(cap)


def gl_disable(
    cap: GLCapabilities,
):
    """disable gl capability"""
    glDisable(cap)


def gl_is_enabled(
    cap: Union[GLCapability, GLFixedFunctionCapability, GLPipelineCapability],
):
    """check if gl_is_enabled capability is enabled"""
    return glIsEnabled(cap)


def toggle_capability(
    enabled: bool,
    capability: Union[GLCapability, GLFixedFunctionCapability, GLPipelineCapability],
):
    """toggle gl_is_enabled capability"""
    if enabled:
        gl_enable(capability)
    else:
        glDisable(capability)
