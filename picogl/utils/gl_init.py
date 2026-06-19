"""
Module for executing sequences of OpenGL tasks in a specified order.

This module provides a utility function to execute a list of OpenGL-related
tasks using a provided backend. Each task is represented by a tuple that includes
an optional message to log and a callable representing the task to be executed.

Classes and Functions:
- execute_gl_tasks: Executes a list of OpenGL task tuples, optionally logging the progress
  or providing step callbacks.
"""

from dataclasses import dataclass
from typing import Callable, Optional

from decologr import Decologr as log
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_CULL_FACE

from picogl.backend.GL.backend import GLBackend
from picogl.backend.legacy.core.camera.setup import enable_blending
from picogl.info import get_gl_info
from picogl.state.draw_mode import GLBitMask


def bind_default_framebuffer() -> None:
    """Bind the window-system default framebuffer (required on some Qt/macOS paths)."""
    from OpenGL.GL import GL_FRAMEBUFFER, glBindFramebuffer

    glBindFramebuffer(GL_FRAMEBUFFER, 0)


def set_clear_color_only(
    backend: GLBackend, color: tuple[float, float, float, float]
) -> None:
    """Set the clear color without clearing (safe before the default FBO is ready)."""
    bind_default_framebuffer()
    backend.frame.set_clear_color(color)


def clear_to_color(backend: GLBackend, color: tuple[float, float, float, float]) -> None:
    """Apply a clear color and clear the color/depth buffers."""
    bind_default_framebuffer()
    backend.frame.set_clear_color(color)
    try:
        backend.frame.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
    except Exception as ex:
        # Qt/macOS may not have a drawable default framebuffer during initializeGL
        # (especially after multisample). paintGL clears each frame once the surface is ready.
        err = getattr(ex, "err", None)
        if err == 1286:
            log.warning(
                "Skipping framebuffer clear (default FBO not ready yet); "
                "will clear on first paintGL",
                silent=True,
            )
            return
        raise


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
    GLTask(
        "✅ Setting clear colour",
        lambda b: clear_to_color(b, (0.2, 0.2, 0.2, 0.0)),
    ),
    GLTask("✅ Setting depth function", lambda b: b.depth.set_depth_func_gl_less()),
    GLTask("✅ Enabling depth test", lambda b: b.depth.set_depth_test(True)),
    GLTask(
        "✅ Enabling face culling",
        lambda b: b.capabilities.set_enabled(GL_CULL_FACE, True),
    ),
]

paint_gl_list = [
    GLTask(
        None,
        lambda b: b.frame.clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER),
    ),
]

modern_init_gl_list = [
    GLTask("✅ Enabling multisampling", lambda b: b.capabilities.enable_multisample()),
    GLTask("✅ Enabling depth test", lambda b: b.depth.set_depth_test(True)),
    GLTask(
        "✅ Setting clear colour",
        lambda b: set_clear_color_only(b, (0.0, 0.0, 0.0, 1.0)),
    ),
    GLTask("✅ Enabling blending", lambda b: enable_blending(b)),
    # glMaterial* / GL_LIGHTING are invalid in Core Profile; modern shaders own lighting.
    GLTask(
        None,
        lambda b: log.header_message(title="OpenGL Information", message=get_gl_info()),
    ),
]
