"""
Module providing classes and utilities for managing OpenGL state and rendering.

This module includes classes for handling rasterization, blending, depth testing,
rendering states, vertex buffers, attribute arrays, clipping planes, and OpenGL
backend implementations. These classes are designed to abstract and encapsulate
detailed OpenGL operations for easier high-level rendering management.
"""

from dataclasses import dataclass, field
from typing import Any

from numpy import ndarray
from OpenGL.GL import (GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1,
                       GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, glDrawElements,
                       glViewport)
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_FLOAT, GL_UNSIGNED_INT, glBlendFunc
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_VERTEX_ARRAY, glColorPointer,
                                          glEnableClientState, glNormalPointer,
                                          glVertexPointer)
from picogl.backend.GL.backend import GLBackend
from picogl.polygon.mode import PolygonMode
from picogl.texture.gltexture import GLTextureDriver


@dataclass(frozen=True)
class RasterState:
    """Raster State"""
    polygon_mode: int = PolygonMode.FILL
    line_width: float = 1.0

    def apply(self, backend: GLBackend):
        backend.set_polygon_mode(GL_FRONT_AND_BACK, self.polygon_mode)
        backend.set_line_width(self.line_width)


class GLStateManager:
    def __init__(self, backend: GLBackend):
        self.backend = backend
        self._caps: dict[int, bool] = {}

    def set_enabled(self, cap: int, enabled: bool) -> None:
        if self._caps.get(cap) == enabled:
            return
        self._caps[cap] = enabled

        if enabled:
            self.backend.enable(cap)
        else:
            self.backend.disable(cap)

    def is_enabled(self, cap: int) -> bool:
        return self._caps.get(cap, False)


@dataclass
class BlendState:
    """Blend State"""
    enabled: bool = False
    src: int = GL_SRC_ALPHA
    dst: int = GL_ONE_MINUS_SRC_ALPHA

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_BLEND, self.enabled)
        if self.enabled:
            glBlendFunc(self.src, self.dst)


@dataclass(frozen=True)
class DepthState:
    """Depth State"""
    enabled: bool = False
    test: bool = True
    write: bool = True

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_BLEND, self.enabled)
        if self.enabled:
            glBlendFunc(self.src, self.dst)


@dataclass(frozen=True)
class RenderState:
    """Render State"""
    raster: RasterState = field(default_factory=RasterState)
    depth: DepthState = field(default_factory=DepthState)
    blend: BlendState = field(default_factory=BlendState)

    cull_face: bool = False
    lighting: bool = False


class RenderStateApplier:
    """Render State Applier"""
    def __init__(self, backend: GLBackend):
        self.backend = backend
        self.current = None

    def apply(self, state: RenderState):
        if self.current == state:
            return

        prev = self.current
        self.current = state

        # --- Raster ---
        if prev is None or prev.raster != state.raster:
            self.backend.set_line_width(state.raster.line_width)
            self.backend.set_polygon_mode(
                GL_FRONT_AND_BACK,
                state.raster.polygon_mode.value
            )

        # --- Depth ---
        if prev is None or prev.depth != state.depth:
            self.backend.set_depth_test(state.depth.test)
            self.backend.set_depth_write(state.depth.write)

        # --- Blend ---
        if prev is None or prev.blend != state.blend:
            self.backend.set_blend(state.blend.enabled)
            if state.blend.enabled:
                self.backend.set_blend_func(
                    state.blend.src,
                    state.blend.dst
                )

        # --- Misc ---
        if prev is None or prev.cull_face != state.cull_face:
            self.backend.set_cull_face(state.cull_face)

        if prev is None or prev.lighting != state.lighting:
            self.backend.set_lighting(state.lighting)


class GLVertexBuffer:
    def __init__(self, data: ndarray):
        self.data = data

    def bind_legacy(self):
        # fallback path
        pass


@dataclass
class GLAttributeArray:
    """GL Attribute Array"""
    size: int
    dtype: Any
    stride: int
    pointer: Any

    def enable_legacy(self, kind):
        glEnableClientState(kind)
        if kind == GL_VERTEX_ARRAY:
            glVertexPointer(self.size, GL_FLOAT, self.stride, self.pointer)
        elif kind == GL_NORMAL_ARRAY:
            glNormalPointer(GL_FLOAT, self.stride, self.pointer)
        elif kind == GL_COLOR_ARRAY:
            glColorPointer(self.size, GL_FLOAT, self.stride, self.pointer)


@dataclass
class GLViewport:
    x: int
    y: int
    width: int
    height: int

    def apply(self):
        glViewport(self.x, self.y, self.width, self.height)


class TestGLMesh:
    """Test GL Mesh"""
    def __init__(self, vertices, indices=None):
        self.vertices = vertices
        self.indices = indices
        self.attributes: list[GLAttributeArray] = []

    def add_attribute(self, attr: GLAttributeArray):
        self.attributes.append(attr)

    def draw(self):
        for attr in self.attributes:
            attr.enable_legacy(GL_VERTEX_ARRAY)  # refine mapping

        if self.indices is not None:
            glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices)

@dataclass
class DrawCommand:
    """Draw Command"""
    mesh: TestGLMesh
    texture: GLTextureDriver | None = None
    state: RenderState | None = None

    def execute(self, state: GLStateManager):
        self.raster.apply(state.backend)
        self.blend.apply(state)

        if self.texture:
            self.texture.bind()

        self.mesh.draw()


@dataclass
class GLClipPlaneState:
    """GL Clipping Plane State"""
    enabled0: bool = False
    enabled1: bool = False

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_CLIP_DISTANCE0, self.enabled0)
        state.set_enabled(GL_CLIP_DISTANCE1, self.enabled1)

