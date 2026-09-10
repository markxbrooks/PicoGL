"""
boolean
"""

from OpenGL.GL import glGetBooleanv

from picogl.boolean import GLBoolean


def gl_get_boolean_value(value) -> GLBoolean:
    """gl_get_boolean_value:"""
    return glGetBooleanv(value)
