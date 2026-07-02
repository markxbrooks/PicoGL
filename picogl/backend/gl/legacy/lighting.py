"""
Provides a utility function for setting up lighting in a legacy OpenGL
rendering context.

This module includes functionality to configure a basic lighting setup
using fixed-function pipeline capabilities. It specifies various lighting
parameters, such as position, ambient, diffuse, and specular components,
as well as the corresponding material properties.

Functions:
- gl_legacy_lighting: Configures the lighting and material parameters
  for a default scene.

"""

from backend.gl.capability import GLFixedFunctionCapability
from backend.gl.light import GLLightSource
from backend.gl.state.fill import GLFace, GLLightParameter
from backend.gl.wrappers.material import gl_material_f, gl_material_fv


def gl_legacy_lighting():
    """Set up lighting"""
    GLLightSource.lightf(
        GLFixedFunctionCapability.LIGHT0,
        GLLightParameter.POSITION,
        [1.0, 1.0, 1.0, 0.0],
    )
    GLLightSource.lightf(
        GLFixedFunctionCapability.LIGHT0, GLLightParameter.AMBIENT, [0.3, 0.3, 0.3, 1.0]
    )
    GLLightSource.lightf(
        GLFixedFunctionCapability.LIGHT0, GLLightParameter.DIFFUSE, [0.8, 0.8, 0.8, 1.0]
    )
    GLLightSource.lightf(
        GLFixedFunctionCapability.LIGHT0,
        GLLightParameter.SPECULAR,
        [1.0, 1.0, 1.0, 1.0],
    )

    # Set up material properties
    gl_material_fv(
        GLFace.FRONT_AND_BACK, GLLightParameter.AMBIENT, [0.2, 0.2, 0.2, 1.0]
    )
    gl_material_fv(
        GLFace.FRONT_AND_BACK, GLLightParameter.DIFFUSE, [0.8, 0.8, 0.8, 1.0]
    )
    gl_material_fv(
        GLFace.FRONT_AND_BACK, GLLightParameter.SPECULAR, [1.0, 1.0, 1.0, 1.0]
    )
    gl_material_f(GLFace.FRONT_AND_BACK, GLLightParameter.SHININESS, 50.0)
