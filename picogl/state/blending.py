"""
A context manager for managing OpenGL blend functionality.

This module provides a context manager to temporarily modify and restore
OpenGL blend settings. It handles enabling or disabling the blend capability
as well as setting the blend function parameters. Upon exiting the context,
the original state and settings are restored.
"""


from contextlib import contextmanager

from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.driver.blend import GLBlendDriver
from picogl.backend.capability import GLPipelineCapability, GLBlendFactor, GLBlendTarget


@contextmanager
def gl_blend(src: GLBlendFactor = GLBlendFactor.SRC_ALPHA, dst: GLBlendFactor = GLBlendFactor.ONE_MINUS_SRC_ALPHA):
    """gl blend context manager"""
    was_enabled = GLCapabilityDriver.is_enabled(GLPipelineCapability.BLEND)
    prev_src = int(GLCapabilityDriver.get_integerv(GLBlendTarget.BLEND_SRC))
    prev_dst = int(GLCapabilityDriver.get_integerv(GLBlendTarget.BLEND_DST))
    """prev_src = glGetIntegerv(GLBlendTarget.BLEND_SRC)
    prev_dst = glGetIntegerv(GLBlendTarget.BLEND_DST)"""

    try:
        if not was_enabled:
            GLCapabilityDriver.enable(GLPipelineCapability.BLEND)
        GLBlendDriver.set_blend_func(src, dst)
        yield
    finally:
        GLBlendDriver.set_blend_func(prev_src, prev_dst)
        if not was_enabled:
            GLCapabilityDriver.disable(GLPipelineCapability.BLEND)
