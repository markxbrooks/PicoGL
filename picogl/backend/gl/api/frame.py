"""
Prepare viewport
"""

from OpenGL.GL import glGenFramebuffers
from OpenGL.raw.GL.VERSION.GL_3_0 import (glBindFramebuffer,
                                          glCheckFramebufferStatus)
# from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.point_size import GLPointCapability
from picogl.backend.gl.enums.target.frame_buffer import GLFrameBufferTarget
from picogl.backend.gl.api.dpr import get_dpr

from elmo.ui.widgets.gl.mol.viewport import Viewport


def prepare_viewport(width: int, height: int, backend: "GLBackend") -> None:
    """
    prepare

    :param width: int
    :param height: int
    :param backend: GLBackend
    :return: None

    Prepares an OpenGL Frame Viewport
    """
    dpr = get_dpr()
    backend.frame.set_viewport(Viewport(0, 0, width * dpr, height * dpr))
    backend.depth.set_depth_test(True)
    backend.frame.set_clear_color(color=(0.1, 0.1, 0.1, 1.0))
    backend.capabilities.enable(GLPointCapability.PROGRAM_POINT_SIZE)
    backend.frame.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)


def gl_bind_framebuffer(
    framebuffer: int, target: GLFrameBufferTarget = GLFrameBufferTarget.FRAMEBUFFER
) -> None:
    """gl_bind_framebuffer"""
    glBindFramebuffer(target, framebuffer)


def gl_check_framebuffer_status(target: GLFrameBufferTarget) -> bool:
    return glCheckFramebufferStatus(target)


def gl_gen_framebuffers(param):
    return glGenFramebuffers(param)
