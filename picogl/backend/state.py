"""
Render-state descriptors and command helpers for PicoGL backends.

The classes in this module are intentionally backend-neutral: they describe
desired OpenGL state and delegate the actual GL calls to a backend object.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from numpy import ndarray
from OpenGL.GL import (
    GL_BLEND,
    GL_CLIP_DISTANCE0,
    GL_CLIP_DISTANCE1,
    GL_DEPTH_TEST,
    GL_FLOAT,
    GL_FRONT_AND_BACK,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    GL_TRIANGLES,
    GL_UNSIGNED_INT,
    glBlendFunc,
    glColorPointer,
    glDrawElements,
    glEnableClientState,
    glNormalPointer,
    glVertexPointer,
    glViewport,
)
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
)

from picogl.backend.capability import BLEND_FACTOR_MAP, CAP_MAP, FACE_MAP
from picogl.polygon.mode import PolygonMode
from picogl.texture.gltexture import GLTextureDriver


def gl_value(value: Any) -> Any:
    """Return a raw OpenGL value for PicoGL enums or pass raw values through."""
    for mapping in (CAP_MAP, BLEND_FACTOR_MAP, FACE_MAP):
        try:
            if value in mapping:
                return mapping[value]
        except TypeError:
            pass

    enum_value = getattr(value, "value", value)
    if isinstance(value, Enum):
        return enum_value
    return value


@dataclass(frozen=True)
class RasterState:
    """Raster State"""

    polygon_mode: int = PolygonMode.FILL
    line_width: float = 1.0

    def apply(self, backend: Any):
        backend.set_polygon_mode(GL_FRONT_AND_BACK, gl_value(self.polygon_mode))
        backend.set_line_width(self.line_width)


class GLStateManager:
    """Tracks capability state without querying OpenGL."""

    def __init__(self, backend: Any):
        self.backend = backend
        self._caps: dict[int, bool] = {}

    def set_enabled(self, cap: int, enabled: bool) -> None:
        cap = gl_value(cap)
        enabled = bool(enabled)
        if self._caps.get(cap) == enabled:
            return
        self._caps[cap] = enabled

        if enabled:
            self.backend.enable(cap)
        else:
            self.backend.disable(cap)

    def is_enabled(self, cap: int) -> bool:
        return self._caps.get(gl_value(cap), False)


@dataclass(frozen=True)
class BlendState:
    """Blend State"""

    enabled: bool = False
    src: int = GL_SRC_ALPHA
    dst: int = GL_ONE_MINUS_SRC_ALPHA

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_BLEND, self.enabled)
        if self.enabled:
            glBlendFunc(gl_value(self.src), gl_value(self.dst))


@dataclass(frozen=True, init=False)
class DepthState:
    """Depth State"""

    test: bool = True
    write: bool = True

    def __init__(
        self,
        test: bool = True,
        write: bool = True,
        enabled: bool | None = None,
    ):
        if enabled is not None:
            test = enabled
        object.__setattr__(self, "test", bool(test))
        object.__setattr__(self, "write", bool(write))

    @property
    def enabled(self) -> bool:
        return self.test

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_DEPTH_TEST, self.test)
        state.backend.set_depth_write(self.write)


@dataclass(frozen=True, init=False)
class RenderState:
    """Flat render-state descriptor with nested-state constructor support."""

    blend: bool = False
    blend_src: int = GL_SRC_ALPHA
    blend_dst: int = GL_ONE_MINUS_SRC_ALPHA
    depth_test: bool = True
    depth_write: bool = True
    line_width: float = 1.0
    polygon_mode: int = PolygonMode.FILL
    cull_face: bool = False
    lighting: bool = False

    def __init__(
        self,
        *,
        raster: RasterState | None = None,
        depth: DepthState | None = None,
        blend: BlendState | bool | None = None,
        blend_src: int = GL_SRC_ALPHA,
        blend_dst: int = GL_ONE_MINUS_SRC_ALPHA,
        depth_test: bool | None = None,
        depth_write: bool | None = None,
        line_width: float | None = None,
        polygon_mode: int | None = None,
        cull_face: bool = False,
        lighting: bool = False,
    ):
        if raster is not None:
            line_width = raster.line_width if line_width is None else line_width
            polygon_mode = (
                raster.polygon_mode if polygon_mode is None else polygon_mode
            )

        if depth is not None:
            depth_test = depth.test if depth_test is None else depth_test
            depth_write = depth.write if depth_write is None else depth_write

        if isinstance(blend, BlendState):
            blend_src = blend.src
            blend_dst = blend.dst
            blend_enabled = blend.enabled
        else:
            blend_enabled = bool(blend) if blend is not None else False

        object.__setattr__(self, "blend", bool(blend_enabled))
        object.__setattr__(self, "blend_src", gl_value(blend_src))
        object.__setattr__(self, "blend_dst", gl_value(blend_dst))
        object.__setattr__(
            self,
            "depth_test",
            True if depth_test is None else bool(depth_test),
        )
        object.__setattr__(
            self,
            "depth_write",
            True if depth_write is None else bool(depth_write),
        )
        object.__setattr__(
            self,
            "line_width",
            1.0 if line_width is None else float(line_width),
        )
        object.__setattr__(
            self,
            "polygon_mode",
            gl_value(PolygonMode.FILL if polygon_mode is None else polygon_mode),
        )
        object.__setattr__(self, "cull_face", bool(cull_face))
        object.__setattr__(self, "lighting", bool(lighting))

    @property
    def raster(self) -> RasterState:
        return RasterState(
            polygon_mode=self.polygon_mode,
            line_width=self.line_width,
        )

    @property
    def depth(self) -> DepthState:
        return DepthState(test=self.depth_test, write=self.depth_write)

    @property
    def blend_state(self) -> BlendState:
        return BlendState(
            enabled=self.blend,
            src=self.blend_src,
            dst=self.blend_dst,
        )


class RenderStateApplier:
    """Applies render-state deltas through a GL backend."""

    def __init__(self, backend: Any):
        self.backend = backend
        self.current: RenderState | None = None

    def apply(self, state: RenderState):
        if self.current == state:
            return

        prev = self.current
        self.current = state

        if prev is None or prev.line_width != state.line_width:
            self.backend.set_line_width(state.line_width)

        if prev is None or prev.polygon_mode != state.polygon_mode:
            self.backend.set_polygon_mode(GL_FRONT_AND_BACK, state.polygon_mode)

        if prev is None or prev.depth_test != state.depth_test:
            self.backend.set_depth_test(state.depth_test)

        if prev is None or prev.depth_write != state.depth_write:
            self.backend.set_depth_write(state.depth_write)

        if prev is None or prev.blend != state.blend:
            self.backend.set_blend(state.blend)

        if state.blend and (
            prev is None
            or prev.blend_src != state.blend_src
            or prev.blend_dst != state.blend_dst
        ):
            self.backend.set_blend_func(state.blend_src, state.blend_dst)

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

    mesh: Any
    mode: int | None = None
    texture: GLTextureDriver | int | None = None
    state: RenderState | None = None

    def execute(self, backend: Any):
        if self.state is not None:
            if hasattr(backend, "apply_state"):
                backend.apply_state(self.state)
            else:
                RenderStateApplier(backend).apply(self.state)

        if self.texture:
            if isinstance(self.texture, int) and hasattr(backend, "bind_texture"):
                backend.bind_texture(self.texture)
            elif hasattr(self.texture, "bind"):
                self.texture.bind()

        if self.mode is not None and hasattr(backend, "draw_mesh"):
            backend.draw_mesh(self.mesh, self.mode)
        elif hasattr(self.mesh, "draw"):
            self.mesh.draw()
        else:
            raise TypeError("DrawCommand requires a mode/backend draw_mesh or a drawable mesh.")


@dataclass
class GLClipPlaneState:
    """GL Clipping Plane State"""

    enabled0: bool = False
    enabled1: bool = False

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_CLIP_DISTANCE0, self.enabled0)
        state.set_enabled(GL_CLIP_DISTANCE1, self.enabled1)


__all__ = [
    "BlendState",
    "DepthState",
    "DrawCommand",
    "GLAttributeArray",
    "GLClipPlaneState",
    "GLStateManager",
    "GLVertexBuffer",
    "GLViewport",
    "RasterState",
    "RenderState",
    "RenderStateApplier",
    "TestGLMesh",
    "gl_value",
]
