"""
Provides a wrapper for the OpenGL glPixelStorei function to set pixel storage modes.

This module includes a function to simplify usage of the OpenGL glPixelStorei API. It allows
the user to specify parameters related to pixel storage during rendering or image transfer.

Functions:
- gl_pixel_store_i: Wrapper for the glPixelStorei function.
"""

from OpenGL.raw.GL.VERSION.GL_1_0 import glPixelStorei


def gl_pixel_store_i(pname: int, param: int):
    """
    Issues an OpenGL command to set pixel packing or unpacking storage modes.

    This function serves as a wrapper for the OpenGL `glPixelStorei` command, which defines the parameters
    affecting the storage of pixel data during read and write operations.

    Parameters:
    pname (int): Specifies the name of the pixel storage parameter to be set. Common options include
    GL_PACK_ALIGNMENT, GL_UNPACK_ALIGNMENT, etc.
    param (int): Specifies the value to be assigned to the parameter indicated by `pname`.
    """
    glPixelStorei(pname, param)
