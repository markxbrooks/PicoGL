"""
Object renderer module.
"""

from pathlib import Path

from decologr import Decologr as log
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.renderer import GLContext, MeshData, RendererBase
from picogl.utils.loader.texture import TextureLoader
from picogl.utils.texture import bind_texture_array


class ObjectRenderer(RendererBase):
    """Unified renderer for textured and untextured objects."""

    def __init__(
        self,
        context: GLContext,
        data: MeshData,
        base_dir: str | Path | None = None,
        glsl_dir: str | Path | None = None,
        use_texture: bool = False,
        texture_file: str | None = None,
        resource_subdir: str = "tu02",
    ):
        super().__init__()
        self.base_dir = base_dir
        self.resource_subdir = resource_subdir
        self.texture_file = texture_file
        self.context = context
        self.data = data
        self.data.vertex_count = len(self.data.vertices.flatten()) // 3
        self.show_model = True
        self.glsl_dir = glsl_dir

        # Texture-related
        self.use_texture = use_texture
        log.parameter("Using texture", use_texture)
        self.texture = None
        if use_texture:
            base_path = Path(base_dir) if base_dir else Path(".")
            resource_path = base_path / "resources" / resource_subdir
            if texture_file:
                texture_path = resource_path / texture_file
                self.texture = TextureLoader(str(texture_path))
                self.context.texture_id = self.texture.texture_glid

    def initialize_shaders(self):
        """Load and compile shaders."""
        log.message("Loading shaders...")
        if not self.context:
            self.context = GLContext()
        self.context.create_shader_program(
            vertex_source_file="vertex.glsl",
            fragment_source_file="fragment.glsl",
            glsl_dir=self.glsl_dir,
        )

    def initialize(self):
        """Create VAO and VBOs once."""
        if self.context.vaos is None:
            self.context.vaos = {}
        model_vao = VertexArrayObject()
        model_vao.add_vbo(index=0, data=self.data.vertices, size=3)

        if self.use_texture and self.data.texcoords is not None:
            model_vao.add_vbo(index=1, data=self.data.texcoords, size=2)
            self.context.vaos["model"] = model_vao
        else:
            # fall back to colors + normals
            if self.data.colors is not None:
                model_vao.add_vbo(index=1, data=self.data.colors, size=3)
            if self.data.normals is not None:
                model_vao.add_vbo(index=2, data=self.data.normals, size=3)
            self.context.vaos["model"] = model_vao

    def render(self) -> None:
        """Dispatch render pass."""
        if self.show_model:
            self._draw_model()
        self._finalize_render()

    def _draw_model(self):
        """Draw the model"""
        model_vao = self.context.vaos["model"]
        shader = self.context.shader
        with shader, model_vao:
            shader.uniform("mvp_matrix", self.context.mvp_matrix)
            shader.uniform("model_matrix", self.context.model_matrix)
            shader.uniform("viewPos", self.context.eye_np)

            if self.use_texture and self.texture:
                bind_texture_array(self.context.texture_id)
                shader.uniform("texture0", 0)

            model_vao.draw(mode=GL_TRIANGLES, index_count=self.data.vertex_count)
