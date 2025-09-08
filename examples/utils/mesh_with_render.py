import numpy as np

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.logger import Logger as log


class MeshWithRender(object):
    def __init__(self):
        """constructor"""
        self.texture = None
        self.shader = None
        self.mesh = None

    def make_context(self):
        """make_context"""
        self.load_shader()
        self.load_object()
        self.load_texture()
        return self

    def load_shader(self):
        """load_shader"""
        self.shader = ShaderProgram()

    def load_object(self):
        """load_object"""
        self.mesh = None
        log.message("Make and fill OpenGL buffers,vertex,uv,normal,tangent,indices")

    def load_texture(self):
        self.texture = None
        log.message("No texture for this object")

    def render(
        self,
        mvp_matrix: np.ndarray = None,
        view_matrix: np.ndarray = None,
        projection_matrix: np.ndarray = None,
    ):
        log.message("override rendering process")
        pass
