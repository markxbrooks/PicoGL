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

from OpenGL.GL import glColorPointer, glDrawElements, glEnableClientState, glNormalPointer, glTexCoordPointer, glVertexPointer

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
    def set_polygon_mode(self, mode: int): ...

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
        bind()   # assumes VAO already configured

    def draw(self, mesh, mode):
        if mesh.ebo is not None:
            glDrawElements(mode, mesh.index_count, GLNumeric.UNSIGNED_INT, None)


