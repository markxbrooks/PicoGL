"""
GL Backend Interface.

This module provides an interface for a GL backend implementation, which
offers functionalities for managing OpenGL state, drawing meshes, managing
materials, handling client-side arrays, and interacting with textures.

Classes:
    GLBackend: A class defining the interface for the GL backend with
               various methods for rendering and managing rendering states.
"""

from abc import ABC, abstractmethod
import warnings
from typing import Any, Protocol, runtime_checkable

from picogl.backend.geometry.factory import (
    GLBindingStrategy,
    LegacyBinding,
    ModernBinding,
)
from picogl.backend.legacy.core.pipeline import (
    GLLegacyPipeline,
    LegacyPipeline,
    LegacyPipelineProtocol,
)

__all__ = [
    "AbstractGLBackend",
    "GLBindingStrategy",
    "GLPipeline",
    "GLLegacyPipeline",
    "LegacyBinding",
    "LegacyPipeline",
    "LegacyPipelineProtocol",
    "ModernBinding",
]


class AbstractGLBackend(ABC):
    """
    ALL rendering must go through this interface.
    """

    @abstractmethod
    def set_blend(self, enabled: bool): ...

    @abstractmethod
    def set_depth_test(self, enabled: bool): ...

    @abstractmethod
    def set_depth_write(self, enabled: bool): ...

    @abstractmethod
    def set_cull_face(self, enabled: bool): ...

    @abstractmethod
    def set_line_width(self, width: float): ...

    @abstractmethod
    def set_polygon_mode(self, *args): ...

    @abstractmethod
    def set_lighting(self, enabled: bool): ...

    @abstractmethod
    def set_uniform_color(self, color: tuple, alpha: float): ...

    @abstractmethod
    def draw_elements(self, mode: int, indices): ...


@runtime_checkable
class GLPipeline(LegacyPipelineProtocol, Protocol):
    """
    Deprecated alias for :class:`LegacyPipelineProtocol`.

    Do not use for new code. Modern rendering uses :class:`~picogl.backend.modern.core.pipeline.ShaderPipeline`.
    """


def _warn_deprecated_glpipeline() -> None:
    warnings.warn(
        "GLPipeline is deprecated; use LegacyPipeline or ShaderPipeline explicitly",
        DeprecationWarning,
        stacklevel=3,
    )
