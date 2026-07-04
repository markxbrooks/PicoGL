from __future__ import annotations

import ctypes

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    glColorPointer,
    glNormalPointer,
    glTexCoordPointer,
    glVertexPointer,
)
from picogl.backend.gl.enums import GLNumeric
from picogl.gpu.buffers.attributes import AttributeSpec


def gl_color_pointer_from_spec(attr: AttributeSpec):
    """gl color pointer"""
    gl_color_array_pointer(
        size=attr.size,
        num_type=attr.type,
        stride=attr.stride,
        pointer=ctypes.c_void_p(attr.offset),
    )


def gl_normal_pointer_from_spec(attr: AttributeSpec):
    """gl normal pointer"""
    gl_normal_array_pointer(
        num_type=attr.type,
        stride=attr.stride,
        pointer=ctypes.c_void_p(attr.offset),
    )


def gl_vertex_pointer_from_spec(attr: AttributeSpec):
    """gl legacy client state"""
    gl_vertex_array_pointer(
        size=attr.size,
        num_type=attr.type,
        stride=attr.stride,
        pointer=ctypes.c_void_p(attr.offset),
    )


def gl_vertex_array_pointer(
    pointer: np.ndarray | int,
    size: int = 3,
    num_type: GLNumeric = GLNumeric.FLOAT,
    stride: int = 0,
):
    """gl vertex pointer for mesh binding."""
    glVertexPointer(size, num_type, stride, pointer)


def gl_normal_array_pointer(
    pointer: np.ndarray,
    stride: int = 0,
    num_type: GLNumeric = GLNumeric.FLOAT,
):
    """gl normal pointer for mesh binding."""
    glNormalPointer(num_type, stride, pointer)


def gl_color_array_pointer(
    pointer: np.ndarray,
    size: int = 4,
    num_type: GLNumeric = GLNumeric.FLOAT,
    stride: int = 0,
):
    """gl color pointer for mesh binding."""
    glColorPointer(size, num_type, stride, pointer)


def gl_texcoord_array_pointer(
    pointer: np.ndarray,
    size: int = 2,
    stride: int = 0,
    num_type: GLNumeric = GLNumeric.FLOAT,
):
    """gl texcoord pointer for mesh binding."""
    glTexCoordPointer(size, num_type, stride, pointer)
