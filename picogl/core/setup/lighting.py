"""
This module provides functionality to set up OpenGL lighting.

The module enables basic lighting features in OpenGL and initializes
a light source with specified properties such as position, ambient,
diffuse, and specular components. It applies these properties to the
primary light in the scene.
"""

from picogl.backend.gl.api.enable import gl_enable_capability_list
from picogl.backend.gl.lighting import LightSource
from picogl.backend.gl.state.fill import GLLight
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


def gl_setup_lighting():
    """Set up lighting"""
    gl_enable_capability_list([GLLight.LIGHTING, GLLight.LIGHT0])
    light = LightSource(
        position=Vec4(1.0, 1.0, 1.0, 0.0),
        ambient=RGBAColor.WHITE.scaled(0.2),
        diffuse=RGBAColor.WHITE.scaled(0.8),
        specular=RGBAColor.WHITE.with_alpha(1.0),
    )
    light.apply(GLLight.LIGHT0)
