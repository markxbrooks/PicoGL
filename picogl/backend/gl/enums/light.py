


from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_LIGHT_MODEL_AMBIENT,
                                          GL_LIGHT_MODEL_LOCAL_VIEWER,
                                          GL_LIGHT_MODEL_TWO_SIDE)


class GLLightModel:
    """
    Manages and represents a light model in an OpenGL-based rendering system.

    This class encapsulates functionality required for handling light-related
    properties in a rendering context. It handles parameters such as lighting
    coefficients, shading styles, and other attributes related to OpenGL's
    light model. It is intended to be used as part of a larger graphics
    pipeline rendering system.
    """
    AMBIENT = GL_LIGHT_MODEL_AMBIENT
    LOCAL_VIEWER = GL_LIGHT_MODEL_LOCAL_VIEWER
    TWO_SIDE = GL_LIGHT_MODEL_TWO_SIDE