"""
Module for executing sequences of OpenGL tasks in a specified order.

This module provides a utility function to execute a list of OpenGL-related
tasks using a provided backend. Each task is represented by a tuple that includes
an optional message to log and a callable representing the task to be executed.

Classes and Functions:
- execute_gl_tasks: Executes a list of OpenGL task tuples, optionally logging the progress
  or providing step callbacks.
"""

from decologr import Decologr as log

from picogl.backend.GL.backend import GLBackend
from picogl.backend.legacy.core.camera.lighting import setup_lighting_mode_zero
from picogl.backend.legacy.core.camera.setup import (enable_blending, enable_smoothing,
                                                     setup_materials)
from picogl.info import get_gl_info
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass(frozen=True)
class GLTask:
    message: Optional[str]
    func: Callable[["GLBackend"], None]


def execute_gl_tasks(
    task_list: list[GLTask],
    backend: GLBackend,
    *,
    on_step: Optional[Callable[[int, int, Optional[str]], None]] = None,
):
    if not isinstance(task_list, list):
        raise TypeError("task_list must be a list of GLTask.")

    total = len(task_list)

    for i, task in enumerate(task_list, start=1):
        if not isinstance(task, GLTask):
            raise TypeError(f"Task #{i} is not a GLTask: {task!r}")

        if task.message:
            log.message(f"[{i}/{total}] {task.message}")

        try:
            task.func(backend)
        except Exception as ex:
            log.error(
                f"Error in task #{i} ({task.message or 'no message'}): {ex}",
                exception=ex,
            )
            raise

        if on_step:
            try:
                on_step(i, total, task.message)
            except Exception:
                pass

legacy_init_gl_list = [
    GLTask("✅ Initializing OpenGL context...", lambda b: None),
    GLTask("✅ Setting clear colour", lambda b: b.clear_grey()),
    GLTask("✅ Setting depth function", lambda b: b.set_depth_func_gl_less()),
    GLTask("✅ Enabling depth test", lambda b: b.enable_depth_test()),
    GLTask("✅ Enabling face culling", lambda b: b.enable_cull_face()),
]

paint_gl_list = [
    GLTask(None, lambda b: b.clear_background()),
]

modern_init_gl_list = [
    GLTask("✅ Enabling multisampling", lambda b: b.enable_multisample()),
    GLTask("✅ Enabling depth test", lambda b: b.enable_depth_test()),
    GLTask("✅ Clearing background", lambda b: b.clear_background()),
    GLTask("✅ Enabling blending", lambda b: enable_blending(b)),
    GLTask("✅ Enabling smoothing", lambda b: enable_smoothing(b)),
    GLTask("✅ Setting up materials", lambda b: setup_materials(b)),
    GLTask("✅ Setting up lighting", lambda b: setup_lighting_mode_zero(b)),
    GLTask(None, lambda b: log.header_message(
        title="OpenGL Information",
        message=get_gl_info()
    )),
]
