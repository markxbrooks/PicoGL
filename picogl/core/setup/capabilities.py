"""
Configure and enable specific OpenGL capabilities.

This function sets up and enables a predefined set of OpenGL capabilities,
which are required for specific rendering behaviors like depth testing
and lighting.

The function utilizes a list of capabilities from different OpenGL
subsystems (pipeline, fixed-function, and state) and enables them
using the `gl_enable` function from the corresponding API.
"""

from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLPipelineCapability, GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLCapability


def gl_setup_capabilities():
    """setup capabilities"""
    capabilities_to_enable = [
        GLPipelineCapability.DEPTH_TEST,
        GLFixedFunctionCapability.LIGHTING,
        GLFixedFunctionCapability.LIGHT0,
        GLCapability.COLOR_MATERIAL
    ]
    for capability in capabilities_to_enable:
        gl_enable(capability)