"""
gl enable disable is enabled
"""

from typing import Union

from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled

from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLPipelineCapability)
from picogl.backend.gl.enums.legacy import GLLegacyClipPlane
from picogl.backend.gl.enums.point_size import (GLLegacyPointCapability,
                                                GLPointCapability)
from picogl.backend.gl.state.fill import GLCapability, GLLight
from picogl.texture.gltexture import GLTexture

GLCapabilities = Union[
    GLCapability,
    GLLegacyPointCapability,
    GLPointCapability,
    GLFixedFunctionCapability,
    GLPipelineCapability,
    GLLegacyClipPlane,
    GLTexture,
    GLLight
]


def gl_enable(
        cap: GLCapabilities,
):
    """enable gl_enable capability"""
    glEnable(cap)


def gl_enable_capability_list(capabilities: list[GLCapabilities]):
    """GL enable capabilities"""
    for cap in capabilities:
        gl_enable(cap)


def gl_disable(cap: GLCapabilities):
    """disable gl capability"""
    glDisable(cap)


def gl_disable_capability_list(capabilities: list[GLCapabilities]):
    """gl disable capabilities"""
    for cap in capabilities:
        gl_disable(cap)


def gl_is_enabled(cap: GLCapabilities):
    """check if gl_is_enabled capability is enabled"""
    return glIsEnabled(cap)


def toggle_capability(enabled: bool,capability: GLCapabilities):
    """toggle gl_is_enabled capability"""
    if enabled:
        gl_enable(capability)
    else:
        glDisable(capability)
