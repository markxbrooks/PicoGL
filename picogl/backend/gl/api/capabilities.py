"""
gl Capabilities
"""

from typing import Union

from picogl.backend.gl.capability import (
    GLFixedFunctionCapability,
    GLPipelineCapability,
)
from picogl.backend.gl.enums.legacy.cliping import GLLegacyClipPlane
from picogl.backend.gl.enums.point_size import (
    GLLegacyPointCapability,
    GLPointCapability,
)
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
    GLLight,
]
