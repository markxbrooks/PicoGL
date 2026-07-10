"""
Enable depth test
"""

from picogl.backend.gl.api.depth import gl_clear_depth
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLPipelineCapability


def enable_depth_test() -> None:
    """
    enable_depth_test

    :return: None
    """
    gl_enable(GLPipelineCapability.DEPTH_TEST)
    gl_clear_depth(1.0)
