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
from typing import Any, Protocol, runtime_checkable

from OpenGL.GL import glColorPointer, glDrawElements, glEnableClientState, glNormalPointer, glTexCoordPointer, glVertexPointer

from picogl.numerical import GLNumeric
from picogl.state.client import GLClientState


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


class GLBindingStrategy(ABC):
    @abstractmethod
    def bind_mesh(self, mesh): ...

    @abstractmethod
    def draw(self, mesh, mode): ...


@runtime_checkable
class GLPipeline(Protocol):
    """Pipeline strategy for fixed-function or modern rendering operations."""

    def set_projection(self, fovy, aspect, znear, zfar): ...
    def translate(self, x, y, z): ...
    def set_light(self, position, light: Any = ...): ...
    def set_material(self, face, material): ...
    def set_uniform_color(self, color, alpha): ...
    def vertex_3f(self, v1): ...
    def tex_coord2f(self, coord): ...
    def set_matrix_mode_projection(self): ...


class LegacyBinding(GLBindingStrategy):
    def bind_mesh(self, mesh):
        if mesh.vertices is not None:
            glEnableClientState(GLClientState.VERTEX)
            glVertexPointer(3, GLNumeric.FLOAT, 0, mesh.vertices)

        if mesh.normals is not None:
            glEnableClientState(GLClientState.NORMAL)
            glNormalPointer(GLNumeric.FLOAT, 0, mesh.normals)

        if mesh.colors is not None:
            glEnableClientState(GLClientState.COLOR)
            glColorPointer(4, GLNumeric.FLOAT, 0, mesh.colors)

        if mesh.texcoords is not None:
            glEnableClientState(GLClientState.COLOR)
            glTexCoordPointer(2, GLNumeric.FLOAT, 0, mesh.texcoords)

    def draw(self, mesh, mode):
        if mesh.indices is not None:
            glDrawElements(mode, len(mesh.indices), GLNumeric.UNSIGNED_INT, mesh.indices)


class ModernBinding(GLBindingStrategy):
    def bind_mesh(self, mesh):
        self.bind()   # assumes VAO already configured

    def draw(self, mesh, mode):
        if mesh.ebo is not None:
            glDrawElements(mode, mesh.index_count, GLNumeric.UNSIGNED_INT, None)


