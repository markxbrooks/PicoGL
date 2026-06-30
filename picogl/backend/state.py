"""
Render-state descriptors and command helpers for PicoGL backends.

The classes in this module are intentionally backend-neutral: they describe
desired OpenGL state and delegate the actual gl calls to a backend object.
"""

from dataclasses import dataclass
from typing import Any, Protocol

from numpy import ndarray
from OpenGL.GL import glBlendFunc, glViewport
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
)

from picogl.backend.gl.capability import (
    GLBlendFactor,
    GLFixedFunctionCapability,
    GLPipelineCapability,
)
from picogl.backend.gl.enums import GLDrawMode, GLIndexType, GLNumeric
from picogl.backend.gl.enums.point_size import GLPointCapability
from picogl.backend.gl.state.fill import GLCapability, GLFace, GLFillMode
from picogl.backend.gl.wrappers import gl_draw_elements, gl_enable_legacy_client_state
from picogl.backend.gl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_normal_array_pointer,
    gl_vertex_array_pointer,
)
from picogl.backend.value import gl_value
from picogl.texture.gltexture_driver import GLTextureDriver


class CapabilityDriver(Protocol):
    """Capability Driver"""

    def enable(self, cap: int) -> None: ...
    def disable(self, cap: int) -> None: ...


@dataclass(frozen=True)
class RasterState:
    """Raster State"""

    polygon_mode: Any = GLFillMode.FILL
    line_width: float = 1.0
    polygon_offset: tuple[float, float] = (0.0, 0.0)
    point_size: float | None = None

    def apply(self, backend: Any) -> None:
        if hasattr(backend, "raster"):
            backend.raster.apply(self)
            return
        if hasattr(backend, "set_line_width"):
            backend.set_polygon_mode(GLFace.FRONT_AND_BACK, gl_value(self.polygon_mode))
            backend.set_line_width(self.line_width)


class GLStateManager:
    """Tracks capability state without querying OpenGL."""

    def __init__(self, backend: CapabilityDriver):
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
    src: Any = GLBlendFactor.SRC_ALPHA
    dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA

    def apply(self, state: GLStateManager):
        backend = state.backend
        if hasattr(backend, "blend"):
            backend.blend.apply(self)
            return
        state.set_enabled(GLPipelineCapability.BLEND, self.enabled)
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
        backend = state.backend
        if hasattr(backend, "depth"):
            backend.depth.apply(self)
            return
        state.set_enabled(GLPipelineCapability.DEPTH_TEST, self.test)
        state.backend.set_depth_write(self.write)


@dataclass(frozen=True, init=False)
class RenderState:
    """Flat render-state descriptor with nested-state constructor support."""

    blend: bool = False
    blend_src: Any = GLBlendFactor.SRC_ALPHA
    blend_dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA
    depth_test: bool = True
    depth_write: bool = True
    line_width: float = 1.0
    polygon_mode: Any = GLFillMode.FILL
    polygon_offset: tuple[float, float] = (0.0, 0.0)
    point_size: float | None = None
    program_point_size: bool = False
    cull_face: bool = False
    lighting: bool = False

    def __init__(
        self,
        *,
        raster: RasterState | None = None,
        depth: DepthState | None = None,
        blend: BlendState | bool | None = None,
        blend_src: Any = GLBlendFactor.SRC_ALPHA,
        blend_dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA,
        depth_test: bool | None = None,
        depth_write: bool | None = None,
        line_width: float | None = None,
        polygon_mode: Any | None = None,
        polygon_offset: tuple[float, float] | None = None,
        point_size: float | None = None,
        program_point_size: bool = False,
        cull_face: bool = False,
        lighting: bool = False,
    ):
        if raster is not None:
            line_width = raster.line_width if line_width is None else line_width
            polygon_mode = raster.polygon_mode if polygon_mode is None else polygon_mode
            polygon_offset = (
                raster.polygon_offset if polygon_offset is None else polygon_offset
            )
            point_size = raster.point_size if point_size is None else point_size

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
        object.__setattr__(self, "blend_src", blend_src)
        object.__setattr__(self, "blend_dst", blend_dst)
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
            GLFillMode.FILL if polygon_mode is None else polygon_mode,
        )
        object.__setattr__(
            self,
            "polygon_offset",
            (0.0, 0.0) if polygon_offset is None else tuple(polygon_offset),
        )
        object.__setattr__(self, "point_size", point_size)
        object.__setattr__(self, "program_point_size", bool(program_point_size))
        object.__setattr__(self, "cull_face", bool(cull_face))
        object.__setattr__(self, "lighting", bool(lighting))

    @property
    def raster(self) -> RasterState:
        return RasterState(
            polygon_mode=self.polygon_mode,
            line_width=self.line_width,
            polygon_offset=self.polygon_offset,
            point_size=self.point_size,
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
    """Applies render-state deltas through a gl backend."""

    def __init__(self, backend: Any):
        self.backend = backend
        self.current: RenderState | None = None

    def apply(self, state: RenderState):
        if self.current == state:
            return

        prev = self.current
        self.current = state

        if prev is None or prev.raster != state.raster:
            self.backend.raster.apply(state.raster)

        if prev is None or prev.depth != state.depth:
            self.backend.depth.apply(state.depth)

        if prev is None or prev.blend_state != state.blend_state:
            self.backend.blend.apply(state.blend_state)

        if prev is None or prev.cull_face != state.cull_face:
            self.backend.capabilities.set_enabled(
                GLPipelineCapability.CULL_FACE,
                state.cull_face,
            )

        # Core-profile contexts reject GL_LIGHTING; modern draws use shader lighting.
        if state.lighting and (prev is None or not prev.lighting):
            self.backend.capabilities.set_enabled(
                GLFixedFunctionCapability.LIGHTING,
                True,
            )

        if state.program_point_size and (prev is None or not prev.program_point_size):

            self.backend.capabilities.enable(GLPointCapability.PROGRAM_POINT_SIZE)
        elif (
            prev is not None
            and prev.program_point_size
            and not state.program_point_size
        ):

            self.backend.capabilities.disable(GLPointCapability.PROGRAM_POINT_SIZE)


class GLVertexBuffer:
    def __init__(self, data: ndarray):
        self.data = data

    def bind_legacy(self):
        # fallback path
        pass


@dataclass
class GLAttributeArray:
    """gl Attribute Array"""

    size: int
    dtype: Any
    stride: int
    pointer: Any

    def enable_legacy(self, kind):
        gl_enable_legacy_client_state(kind)
        if kind == GL_VERTEX_ARRAY:
            gl_vertex_array_pointer(
                pointer=self.pointer,
                size=self.size,
                num_type=GLNumeric.FLOAT,
                stride=self.stride,
            )
        elif kind == GL_NORMAL_ARRAY:
            gl_normal_array_pointer(
                pointer=self.pointer,
                num_type=GLNumeric.FLOAT,
                stride=self.stride,
            )
        elif kind == GL_COLOR_ARRAY:
            gl_color_array_pointer(
                pointer=self.pointer,
                size=self.size,
                num_type=GLNumeric.FLOAT,
                stride=self.stride,
            )


@dataclass
class GLViewport:
    x: int
    y: int
    width: int
    height: int

    def apply(self):
        glViewport(self.x, self.y, self.width, self.height)


class TestGLMesh:
    """Test gl Mesh"""

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
            gl_draw_elements(
                len(self.indices),
                GLIndexType.UNSIGNED_INT,
                GLDrawMode.TRIANGLES,
                pointer=self.indices,
            )


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
            if isinstance(self.texture, int) and hasattr(backend, "textures"):
                backend.textures.bind_texture(self.texture)
            elif isinstance(self.texture, int) and hasattr(backend, "bind_texture"):
                backend.bind_texture(self.texture)
            elif hasattr(self.texture, "bind"):
                self.texture.bind()

        if self.mode is not None and hasattr(backend, "geometry"):
            backend.geometry.draw_mesh(self.mesh, self.mode)
        elif self.mode is not None and hasattr(backend, "draw_mesh"):
            backend.draw_mesh(self.mesh, self.mode)
        elif hasattr(self.mesh, "draw"):
            self.mesh.draw()
        else:
            raise TypeError(
                "DrawCommand requires a mode/backend draw_mesh or a drawable mesh."
            )


@dataclass
class GLClipPlaneState:
    """gl Clipping Plane State"""

    enabled0: bool = False
    enabled1: bool = False
    plane0: bool = False
    plane1: bool = False

    def apply(self, state: GLStateManager):
        state.set_enabled(GLCapability.CLIP_DISTANCE0, self.enabled0)
        state.set_enabled(GLCapability.CLIP_DISTANCE1, self.enabled1)


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
