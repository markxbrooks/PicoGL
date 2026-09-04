"""
Provides light model constants from OpenGL.

This module defines constants used for configuring the light model in an
OpenGL rendering context. These constants are imported from OpenGL's GL_1_0
version and represent various parameters that influence light behavior
in rendering.

Constants:
    GL_LIGHT_MODEL_AMBIENT: Represents the ambient light intensity in the
    OpenGL light model.

    GL_LIGHT_MODEL_LOCAL_VIEWER: Represents whether to enable the local
    viewer model in OpenGL lighting.

    GL_LIGHT_MODEL_TWO_SIDE: Indicates whether lighting calculations should
    be performed on both sides of polygons.
"""

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
