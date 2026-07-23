"""
setup capabilities
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