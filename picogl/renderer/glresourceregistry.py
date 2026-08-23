"""
GL Resource Registry

Holds OpenGL-related state (VAOs, shaders, textures, transform matrices)
and tracks resources per Qt / GL context when PySide6 is already in use.

Heavy deps (VertexArrayObject, ShaderProgram, PySide6) are not imported at
module load so GLUT examples stay free of Qt / NumPy-shiboken warnings.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, TypeVar
from weakref import WeakKeyDictionary

import numpy as np
from decologr import Decologr as log

from picogl.shaders import ShaderType

if TYPE_CHECKING:
    from picogl.backend.modern.core.shader.program import ShaderProgram
    from picogl.backend.modern.core.vertex.array.object import VertexArrayObject

T = TypeVar("T")


def _current_qt_context():
    """Return the current Qt GL context if PySide6 is already imported.

    Does not import PySide6 itself — GLUT paths must stay Qt-free.
    """
    qtgui = sys.modules.get("PySide6.QtGui")
    if qtgui is None:
        return None
    qctx = getattr(qtgui, "QOpenGLContext", None)
    if qctx is None:
        return None
    try:
        return qctx.currentContext()
    except Exception:
        return None


class GLResourceRegistry:
    """OpenGL resource registry and render-state holder."""

    def __init__(self):
        self._creation_context = _current_qt_context()
        log.message(
            f"gl context :{id(self._creation_context)}", scope="GLResourceRegistry"
        )
        self._contexts = WeakKeyDictionary()
        self._cache: dict[object, object] = {}
        self._creation_thread_id = threading.get_ident()

        self.vaos: dict[str, VertexArrayObject] = {}
        self.current_vao: Optional[VertexArrayObject] = None

        self.shader: Optional[ShaderProgram] = None
        self.shader_type: ShaderType = ShaderType.DEFAULT

        self.textures: dict[str, int] = {}
        self.active_texture: Optional[str] = None
        self.texture_id: Optional[int] = None

        self.model_matrix = np.identity(4, dtype=np.float32)
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.projection_matrix = np.identity(4, dtype=np.float32)
        self.mvp_matrix = np.identity(4, dtype=np.float32)
        self.eye_position = np.zeros(3, dtype=np.float32)
        self.eye_np = np.zeros(3, dtype=np.float32)

        # Set by GlutRendererWindow.calculate_mvp_matrix (glm types / products)
        self.projection = None
        self.view = None
        self.eye = None
        self.center = None
        self.up = None

    def create_shader_program(
        self,
        vertex_source_file: str,
        fragment_source_file: str,
        glsl_dir: str | Path | None = None,
    ) -> None:
        """Compile and store a vertex/fragment shader program on this registry."""
        from picogl.backend.modern.core.shader.program import ShaderProgram

        self.shader = ShaderProgram(
            shader_name=f"{vertex_source_file}+{fragment_source_file}",
        )
        self.shader.init_shader_from_glsl_files(
            vertex_source_file=vertex_source_file,
            fragment_source_file=fragment_source_file,
            glsl_dir=glsl_dir,
        )

    @property
    def context(self):
        return self._creation_context

    def _get_bucket(self, ctx):
        if ctx is None:
            return {
                "vao": set(),
                "vbo": set(),
                "shader": set(),
                "ebo": set(),
            }
        if ctx not in self._contexts:
            self._contexts[ctx] = {
                "vao": set(),
                "vbo": set(),
                "shader": set(),
                "ebo": set(),
            }
        return self._contexts[ctx]

    def register(self, ctx, resource_type: str, resource):
        if ctx is None:
            return
        bucket = self._get_bucket(ctx)
        bucket[resource_type].add(resource)

    def unregister(self, ctx, resource_type: str, resource):
        if ctx is None:
            return
        bucket = self._get_bucket(ctx)
        bucket[resource_type].discard(resource)

    def get_context_resources(self, ctx):
        if ctx is None:
            return None
        return self._contexts.get(ctx, None)

    def validate_context(self):
        # No Qt loaded, or registry created under GLUT: nothing to check.
        if "PySide6.QtGui" not in sys.modules:
            return
        ctx = _current_qt_context()
        if self._creation_context is None:
            return

        if ctx is None:
            raise RuntimeError("No current OpenGL context")

        if ctx != self._creation_context:
            raise RuntimeError("VAO used in a different OpenGL context")

    def get_context_key(self, ctx):
        if ctx is None:
            return None
        return ctx

    def get_or_create(self, key: object, factory: Callable[[], T]) -> T:
        """Return a cached GL resource, creating it with *factory* if needed."""
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]
