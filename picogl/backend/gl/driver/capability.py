"""
A module for managing OpenGL capabilities, including enabling, disabling,
and querying the state of various capabilities.

This module provides functionality to interact with OpenGL capabilities
through methods for toggling specific features, checking their current state,
and managing multisampling.

Classes:
    GLCapabilityDriver: Encapsulates OpenGL capability management, allowing
    operations such as enabling/disabling features and querying their states.
"""

from OpenGL.raw.GL.VERSION.GL_1_3 import GL_MULTISAMPLE
from picogl.backend.gl.wrappers.enable import gl_disable, gl_enable, gl_is_enabled
from picogl.backend.gl.wrappers.get_integerv import gl_get_integerv
from picogl.backend.state import gl_value


class GLCapabilityDriver:
    """OpenGL capability toggles and queries."""

    @staticmethod
    def enable(cap):
        gl_enable(gl_value(cap))

    @staticmethod
    def disable(cap):
        gl_disable(gl_value(cap))

    def set_enabled(self, cap, enabled: bool):
        self.enable(cap) if enabled else self.disable(cap)

    @staticmethod
    def is_enabled(cap) -> bool:
        return bool(gl_is_enabled(gl_value(cap)))

    @staticmethod
    def get_integerv(val: int):
        result = gl_get_integerv(gl_value(val))
        if hasattr(result, "__len__") and len(result) == 1:
            return int(result[0])
        return result

    def enable_multisample(self):
        self.enable(GL_MULTISAMPLE)
