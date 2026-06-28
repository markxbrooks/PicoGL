"""
gl enable disable is enabled
"""
from typing import Union

from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled

from picogl.backend.gl.capability import GLFixedFunctionCapability, GLPipelineCapability
from picogl.backend.gl.enums.point_size import GLPointCapability, GLLegacyPointCapability
from picogl.backend.gl.state.fill import GLCapability


def gl_enable(cap: Union[GLCapability, GLLegacyPointCapability, GLPointCapability, GLFixedFunctionCapability, GLPipelineCapability]):
    glEnable(cap)


def gl_disable(cap: Union[GLCapability, GLLegacyPointCapability, GLPointCapability, GLFixedFunctionCapability, GLPipelineCapability]):
    glDisable(cap)


def gl_is_enabled(cap: Union[GLCapability, GLFixedFunctionCapability, GLPipelineCapability]):
    return glIsEnabled(cap)


def toggle_capability(enabled: bool, capability: Union[GLCapability, GLFixedFunctionCapability, GLPipelineCapability]):
    if enabled:
        gl_enable(capability)
    else:
        glDisable(capability)