"""Geometry binding layer: CPU mesh data to GPU draw units."""

from picogl.backend.geometry.adapter import DrawableBufferAdapter
from picogl.backend.geometry.factory import (GLBindingStrategy, LegacyBinding,
                                             ModernBinding)
from picogl.backend.geometry.legacy_mesh import LegacyMesh
from picogl.backend.geometry.mesh import GPUMesh
from picogl.backend.geometry.modern_mesh import ModernMesh

__all__ = [
    "DrawableBufferAdapter",
    "GLBindingStrategy",
    "GPUMesh",
    "LegacyBinding",
    "LegacyMesh",
    "ModernBinding",
    "ModernMesh",
]
