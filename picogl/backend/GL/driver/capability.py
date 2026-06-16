from OpenGL.raw.GL.VERSION.GL_1_0 import glDisable, glEnable, glIsEnabled
from OpenGL.raw.GL.VERSION.GL_1_3 import GL_MULTISAMPLE

from picogl.backend.state import gl_value


class GLCapabilityDriver:
    """OpenGL capability toggles and queries."""

    @staticmethod
    def enable(cap):
        glEnable(gl_value(cap))

    @staticmethod
    def disable(cap):
        glDisable(gl_value(cap))

    def set_enabled(self, cap, enabled: bool):
        self.enable(cap) if enabled else self.disable(cap)

    @staticmethod
    def is_enabled(cap) -> bool:
        return bool(glIsEnabled(gl_value(cap)))

    def enable_multisample(self):
        self.enable(GL_MULTISAMPLE)

