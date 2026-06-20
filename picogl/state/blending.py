from contextlib import contextmanager

from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.GL.driver.blend import GLBlendDriver
from picogl.backend.capability import GLPipelineCapability
from picogl.wrappers.get_integerv import gl_get_integerv


@contextmanager
def gl_blend(src=GLBlendFactor.SRC_ALPHA, dst=GLBlendFactor.ONE_MINUS_SRC_ALPHA):
    """gl blend context manager"""
    capabilities = GLCapabilityDriver()
    was_enabled = GLCapabilityDriver.is_enabled(GLPipelineCapability.BLEND)
    prev_src = gl_get_integerv(GLBlendTarget.BLEND_SRC)
    prev_dst = gl_get_integerv(GLBlendTarget.BLEND_DST)

    try:
        if not was_enabled:
            GLCapabilityDriver.enable(GLPipelineCapability.BLEND)
        GLBlendDriver.set_blend_func(src, dst)
        yield
    finally:
        GLBlendDriver.set_blend_func(prev_src, prev_dst)
        if not was_enabled:
            capabilities.disable(GLPipelineCapability.BLEND)
