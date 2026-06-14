"""
Module for executing sequences of OpenGL tasks in a specified order.

This module provides a utility function to execute a list of OpenGL-related
tasks using a provided backend. Each task is represented by a tuple that includes
an optional message to log and a callable representing the task to be executed.

Classes and Functions:
- execute_gl_tasks: Executes a list of OpenGL task tuples, optionally logging the progress
  or providing step callbacks.
"""

from typing import Callable, Optional

from decologr import Decologr as log

from picogl.backend.GL.backend import GLBackend
from picogl.backend.legacy.core.camera.lighting import setup_lighting
from picogl.backend.legacy.core.camera.setup import (enable_blending,
                                                     enable_depth_test,
                                                     enable_smoothing,
                                                     setup_materials)
from picogl.info import get_gl_info


def execute_gl_tasks(
    task_list: list[tuple[str, Callable]], backend: GLBackend,
    *,
    on_step: Optional[Callable[[int, int, Optional[str]], None]] = None,
):
    """
    Execute a sequence of OpenGL-related tasks.

    Each task is a tuple ``(message, func)``:
    - ``message`` (*str* or ``None``): If a string, it is logged before running the task.
      If ``None``, no log message is emitted for that step.
    - ``func`` (*callable*): The function to execute.

    :param task_list:
        A list of ``(message, callable)`` tuples describing the tasks to run.
    :type task_list: list[tuple[str | None, callable]]
    :param on_step:
        Optional ``callback(step_index, total_steps, message)`` after each task is
        scheduled (1-based index). ``message`` may be ``None``.

    :param backend:
        A Renderer Backend eg GLBackend, which is used to create a window and

    :raises TypeError:
        If ``task_list`` is not a list or any element is not a 2-tuple.
    :raises Exception:
        Logs and re-raises any exception thrown by a task.
    """
    if not isinstance(task_list, list):
        raise TypeError("task_list must be a list of (message, callable) tuples.")

    for i, task in enumerate(task_list, start=1):
        if not (isinstance(task, tuple) and len(task) == 2):
            log.error(
                f"Task #{i} is invalid. Expected tuple (str|None, callable), got {task!r}"
            )
            continue

        message, func = task

        if message is not None and not isinstance(message, str):
            log.error(
                f"Task #{i} skipped: message must be str or None, got {type(message).__name__}"
            )
            continue

        if not callable(func):
            log.error(
                f"Task #{i} skipped: second element must be callable, got {type(func).__name__}"
            )
            continue

        if message:
            log.message(f"[{i}/{len(task_list)}] {message}")

        try:
            func()
        except Exception as ex:
            log.error(
                f"Error in task #{i} ({message or 'no message'}): {ex}",
                exception=ex,
            )
            raise

        if on_step is not None:
            try:
                on_step(i, len(task_list), message)
            except Exception:
                pass




init_gl_list = [
    ("✅ Initializing OpenGL context...", lambda: None),  # Message only
    ("✅ Setting clear colour", lambda: backend.clear_grey()),
    ("✅ Setting depth function", lambda: backend.set_depth_func_gl_less()),
    ("✅ Enabling depth test", lambda: backbend.enable_depth_test()),
    ("✅ Enabling face culling", lambda: backbend.enable_cull_face()),
]

paint_gl_list = [
    (
        None,
        lambda: backend.framebuffer.clear_background(),
    ),
]



initialize_gl_list = [
    ("✅ Enabling multisampling", lambda: backend.enable_multisample()),
    ("✅ Enabling depth test", enable_depth_test),
    ("✅ Clearing background ", lambda: backend.clear()),
    ("✅ Enabling blending", enable_blending),
    ("✅ Enabling smoothing", enable_smoothing),
    ("✅ Setting up materials", setup_materials),
    ("✅ Setting up lighting", setup_lighting),
    (None, lambda: log.header_message(title="OpenGL Information",  message=get_gl_info())),
]
