from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from numpy import dtype, generic, ndarray
from OpenGL import GL
from OpenGL.GL import (GL_CLIP_DISTANCE0, GL_CLIP_DISTANCE1,
                       GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
                       GL_DEPTH_COMPONENT, GL_FILL, GL_LINE, GL_MULTISAMPLE, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_TEXTURE_2D,
                       glBindTexture,
                       glClearColor, glDrawElements, glReadPixels, glTexCoordPointer, glViewport)
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_FLOAT, GL_UNSIGNED_INT, glBlendFunc,
                                          glDisable, glEnable,
                                          glIsEnabled, glLineWidth,
                                          glPolygonMode, glTexCoord2f,
                                          glVertex3f)
from OpenGL.raw.GL.VERSION.GL_1_1 import (GL_COLOR_ARRAY, GL_NORMAL_ARRAY,
                                          GL_TEXTURE_COORD_ARRAY,
                                          GL_VERTEX_ARRAY, glColorPointer,
                                          glDeleteTextures,
                                          glEnableClientState, glNormalPointer,
                                          glVertexPointer)
from picogl.backend.opengl import GLBackend
from picogl.state.texture import TexCoord2f
from picogl.texture.gltexture import GLTexture2D


class PolygonMode(Enum):
    FILL = GL_FILL
    LINE = GL_LINE


@dataclass
class RasterState:
    polygon_mode: int = GL_FILL
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
    enabled: bool = False
    src: int = GL_SRC_ALPHA
    dst: int = GL_ONE_MINUS_SRC_ALPHA

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_BLEND, self.enabled)
        if self.enabled:
            glBlendFunc(self.src, self.dst)


@dataclass(frozen=True)
class RasterState:
    polygon_mode: int = GL_FILL
    line_width: float = 1.0


@dataclass(frozen=True)
class BlendState:
    enabled: bool = False
    src: int = GL_SRC_ALPHA
    dst: int = GL_ONE_MINUS_SRC_ALPHA


@dataclass(frozen=True)
class DepthState:
    test: bool = True
    write: bool = True


@dataclass(frozen=True)
class RenderState:
    raster: RasterState = field(default_factory=RasterState)
    depth: DepthState = field(default_factory=DepthState)
    blend: BlendState = field(default_factory=BlendState)

    cull_face: bool = False
    lighting: bool = False


class RenderStateApplier:
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


class LegacyGLBackend(GLBackend):
    """Legacy GL Backend"""

    def read_pixels(self, depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]], x: int, y_gl: int):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)

    def enable_vertex_array(self):
        glEnableClientState(GL_VERTEX_ARRAY)

    def set_vertex_pointer(self, data):
        glVertexPointer(3, GL_FLOAT, 0, data)

    def enable_normal_array(self):
        glEnableClientState(GL_NORMAL_ARRAY)

    def set_normal_pointer(self, data):
        glNormalPointer(GL_FLOAT, 0, data)

    def enable_color_array(self):
        glEnableClientState(GL_COLOR_ARRAY)

    def set_color_pointer(self, data, size):
        glColorPointer(size, GL_FLOAT, 0, data)

    def enable_texcoord_array(self):
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    def set_texcoord_pointer(self, data):
        """set texcoord pointer"""
        glTexCoordPointer(2, GL_FLOAT, 0, data)

    def draw_elements(self, mode, indices):
        """draw elements"""
        glDrawElements(mode, len(indices), GL_UNSIGNED_INT, indices)

    def bind_texture(self, texture_id):
        """bind texture"""
        glBindTexture(GL_TEXTURE_2D, texture_id)

    @staticmethod
    def tex_coord2f(coord: TexCoord2f):
        return glTexCoord2f(coord.u, coord.v)

    @staticmethod
    def tex_coords(t1):
        glTexCoord2f(t1[0], t1[1])

    @staticmethod
    def vertex_3f(v1):
        glVertex3f(v1[0], v1[1], v1[2])

    def is_enabled(self, cap):
        """is enabled"""
        return bool(glIsEnabled(cap))

    def set_blend_func(self, src, dst):
        """set blend function"""
        glBlendFunc(src, dst)

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])

    def set_blend(self, enabled: bool):
        self.enable(GL.GL_BLEND) if enabled else self.disable(GL.GL_BLEND)

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def set_depth_test(self, enabled: bool):
        (
            self.enable(GL.GL_DEPTH_TEST)
            if enabled
            else self.disable(GL.GL_DEPTH_TEST)
        )

    def set_depth_write(self, enabled: bool):
        GL.glDepthMask(bool(enabled))

    def set_cull_face(self, enabled: bool):
        (
            self.enable(GL.GL_CULL_FACE)
            if enabled
            else self.disable(GL.GL_CULL_FACE)
        )

    def set_polygon_mode(self, face, mode):
        glPolygonMode(face, mode)

    def set_lighting(self, enabled: bool):
        (
            self.enable(GL.GL_LIGHTING)
            if enabled
            else self.disable(GL.GL_LIGHTING)
        )

    def set_uniform_color(self, color: tuple, alpha: float):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))


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
    texture: GLTexture2D | None = None
    state: RenderState | None = None

    def execute(self, state: GLStateManager):
        self.raster.apply(state.backend)
        self.blend.apply(state)

        if self.texture:
            self.texture.bind()

        self.mesh.draw()


@dataclass
class GLClipPlaneState:
    enabled0: bool = False
    enabled1: bool = False

    def apply(self, state: GLStateManager):
        state.set_enabled(GL_CLIP_DISTANCE0, self.enabled0)
        state.set_enabled(GL_CLIP_DISTANCE1, self.enabled1)


class GLReadback:
    @staticmethod
    def read_depth(x, y, w, h):
        return glReadPixels(x, y, w, h, GL_DEPTH_COMPONENT, GL_FLOAT)


class ModernGLBackend(GLBackend, ABC):
    """Legacy GL Backend"""

    def viewport(self, x, y, width, height):
        glViewport(x, y, width, height)

    def enable_multisample(self):
        glEnable(GL_MULTISAMPLE)

    def clear_background(self):
        self.clear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def read_pixels(self, depth: ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]], x: int, y_gl: int):
        glReadPixels(x, y_gl, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, depth)

    def enable_clip0(self):
        self.enable(GL_CLIP_DISTANCE0)

    def enable_clip1(self):
        self.enable(GL_CLIP_DISTANCE1)

    def clear_color(self, clear_color):
        glClearColor(*clear_color)

    def disable(self, cap):
        glDisable(cap)

    def set_line_width(self, width):
        glLineWidth(width)

    def set_polygon_mode(self, face, mode):
        glPolygonMode(face, mode)

    def enable_vertex_array(self):
        glEnableClientState(GL_VERTEX_ARRAY)

    def set_vertex_pointer(self, data):
        glVertexPointer(3, GL_FLOAT, 0, data)

    def enable_normal_array(self):
        glEnableClientState(GL_NORMAL_ARRAY)

    def set_normal_pointer(self, data):
        glNormalPointer(GL_FLOAT, 0, data)

    def enable_color_array(self):
        glEnableClientState(GL_COLOR_ARRAY)

    def set_color_pointer(self, data, size):
        glColorPointer(size, GL_FLOAT, 0, data)

    def enable_texcoord_array(self):
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    def set_texcoord_pointer(self, data):
        """set texcoord pointer"""
        glTexCoordPointer(2, GL_FLOAT, 0, data)

    def draw_elements(self, mode, indices):
        """draw elements"""
        glDrawElements(mode, len(indices), GL_UNSIGNED_INT, indices)

    def bind_texture(self, texture_id):
        """bind texture"""
        glBindTexture(GL_TEXTURE_2D, texture_id)

    @staticmethod
    def tex_coord2f(coord: TexCoord2f):
        return glTexCoord2f(coord.u, coord.v)

    @staticmethod
    def tex_coords(t1):
        glTexCoord2f(t1[0], t1[1])

    @staticmethod
    def vertex_3f(v1):
        glVertex3f(v1[0], v1[1], v1[2])

    def is_enabled(self, cap):
        """is enabled"""
        return bool(glIsEnabled(cap))

    def set_blend_func(self, src, dst):
        """set blend function"""
        glBlendFunc(src, dst)

    def delete_texture(self, tex_id: int):
        glDeleteTextures([tex_id])

    def set_blend(self, enabled: bool):
        self.enable(GL.GL_BLEND) if enabled else self.disable(GL.GL_BLEND)

    def set_depth_test(self, enabled: bool):
        (
            self.enable(GL.GL_DEPTH_TEST)
            if enabled
            else self.disable(GL.GL_DEPTH_TEST)
        )

    def set_depth_write(self, enabled: bool):
        GL.glDepthMask(bool(enabled))

    def set_cull_face(self, enabled: bool):
        (
            self.enable(GL.GL_CULL_FACE)
            if enabled
            else self.disable(GL.GL_CULL_FACE)
        )

    def set_lighting(self, enabled: bool):
        (
            self.enable(GL.GL_LIGHTING)
            if enabled
            else self.disable(GL.GL_LIGHTING)
        )

    def set_uniform_color(self, color: tuple, alpha: float):
        r, g, b = color[:3]
        self.set_color((r, g, b, 1.0 - alpha))

