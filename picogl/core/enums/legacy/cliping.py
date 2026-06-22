from enum import IntEnum

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_CLIP_PLANE0, GL_CLIP_PLANE1


class GLLegacyClipPlane(IntEnum):
    """Clipping Mode"""

    CLIP_PLANE0 = GL_CLIP_PLANE0
    CLIP_PLANE1 = GL_CLIP_PLANE1