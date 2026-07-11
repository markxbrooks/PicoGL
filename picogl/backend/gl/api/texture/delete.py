"""
Textures deletion
"""

from OpenGL.GL import glDeleteTextures


def gl_delete_textures(textures: list):
    """delete list of texture"""
    glDeleteTextures(textures)
