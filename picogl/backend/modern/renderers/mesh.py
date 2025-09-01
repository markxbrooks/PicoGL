import numpy as np


class ShaderMeshRenderer:
    """Base class for a renderable mesh with shader and texture."""

    def __init__(self, mesh=None, shader=None, texture=None):
        self.mesh = mesh
        self.shader = shader
        self.texture = texture

    def make_context(self):
        self.load_shader()
        self.load_mesh()
        self.load_texture()
        return self

    def load_shader(self):
        """Load or compile the shader program."""
        self.shader = Shader()  # placeholder

    def load_mesh(self):
        """Load mesh and setup OpenGL buffers (VAO, VBO, EBO)."""
        raise NotImplementedError("Subclass must implement load_mesh()")

    def load_texture(self):
        """Load texture (optional)."""
        self.texture = None  # subclasses may override

    def render(self, mvp_matrix: np.ndarray, view_matrix: np.ndarray, projection_matrix: np.ndarray):
        """Render the object. Subclasses should override this."""
        raise NotImplementedError("Subclass must implement render()")

    def cleanup(self):
        """Free OpenGL resources."""
        if self.texture:
            self.texture.delete()
        if self.shader:
            self.shader.delete()
