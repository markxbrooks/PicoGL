"""GLUT backend wrappers for window init, callbacks, and primitives."""

from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.cube import glut_wire_cube
from picogl.backend.glut.display import (glut_display_func, glut_idle_func,
                                         glut_keyboard_func, glut_motion_func,
                                         glut_mouse_func, glut_post_redisplay,
                                         glut_reshape_func)
from picogl.backend.glut.enums import (GLUTDisplayMode, GLUTMouseButton,
                                       GLUTMouseState)
from picogl.backend.glut.init import (glut_create_window, glut_init,
                                      glut_init_display_mode,
                                      glut_init_window_size, glut_main_loop)
from picogl.backend.glut.teapot import glut_solid_teapot, glut_wire_teapot

__all__ = [
    "GLUTDisplayMode",
    "GLUTMouseButton",
    "GLUTMouseState",
    "glut_create_window",
    "glut_display_func",
    "glut_idle_func",
    "glut_init",
    "glut_init_display_mode",
    "glut_init_window_size",
    "glut_keyboard_func",
    "glut_main_loop",
    "glut_motion_func",
    "glut_mouse_func",
    "glut_post_redisplay",
    "glut_reshape_func",
    "glut_solid_teapot",
    "glut_swap_buffers",
    "glut_wire_cube",
    "glut_wire_teapot",
]
