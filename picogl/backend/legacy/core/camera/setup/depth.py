"""
Enable depth test
"""

from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.wrappers.depth import gl_clear_depth
from picogl.backend.gl.wrappers.enable import gl_enable


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    gl_enable(GLPipelineCapability.DEPTH_TEST)
    gl_clear_depth(1.0)
