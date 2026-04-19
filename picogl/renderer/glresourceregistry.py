"""
GL Context Class
"""
from decologr import Decologr as log
import threading
from dataclasses import field
from typing import Optional
from weakref import WeakKeyDictionary

import numpy as np
from PySide6.QtGui import QOpenGLContext

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.shaders import ShaderType


class GLResourceRegistry:
    """GL Resource Registry"""

    def __init__(self):
        self._creation_context = QOpenGLContext.currentContext()
        log.message(f"Current GL context :{id(self._creation_context)}", scope="GLResourceRegistry")
        self._contexts = WeakKeyDictionary()
        self.vaos: dict[str, VertexArrayObject] = field(default_factory=dict)
        self.current_vao: Optional[VertexArrayObject] = None
        self._creation_thread_id = threading.get_ident()

        self.shader_type: ShaderType = ShaderType.DEFAULT

        self.textures: dict[str, int] = field(default_factory=dict)
        self.active_texture: Optional[str] = None

        self.model_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))
        self.view_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))
        self.projection_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))
        self.eye_position: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))

    @property
    def context(self):
        return self._creation_context

    def _get_bucket(self, ctx):
        if ctx not in self._contexts:
            self._contexts[ctx] = {
                "vao": set(),
                "vbo": set(),
                "shader": set(),
                "ebo": set(),
            }
        return self._contexts[ctx]

    def register(self, ctx, resource_type: str, resource):
        bucket = self._get_bucket(ctx)
        bucket[resource_type].add(resource)

    def unregister(self, ctx, resource_type: str, resource):
        bucket = self._get_bucket(ctx)
        bucket[resource_type].discard(resource)

    def get_context_resources(self, ctx):
        return self._contexts.get(ctx, None)

    def validate_context(self):
        ctx = QOpenGLContext.currentContext()

        if ctx is None:
            raise RuntimeError("No current OpenGL context")

        if self._creation_context is None:
            raise RuntimeError("Resource has no creation context")

        if ctx != self._creation_context:
            raise RuntimeError("VAO used in a different OpenGL context")

    def get_context_key(self, ctx):
        if ctx is None:
            return None
        return ctx  # simple version


