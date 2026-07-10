"""
boolean
"""

from OpenGL.GL import glGetBooleanv


def gl_get_boolean_value(value):
    return glGetBooleanv(value)
