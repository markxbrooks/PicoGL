"""
Object Window for displaying Mesh Data
"""

from pathlib import Path

from picogl.renderer import GLResourceRegistry, MeshData
from picogl.renderer.object import ObjectRenderer
from picogl.ui.backend.glut.window.glut import GlutRendererWindow


class RenderWindow(GlutRendererWindow):
    """Unified render window supporting textured or untextured rendering."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "RenderWindow",
        data: MeshData | None = None,
        base_dir: str | Path | None = None,
        glsl_dir: str | Path | None = None,
        use_texture: bool = False,
        texture_file: str | None = None,
        resource_subdir: str = "tu02",
        *args,
        **kwargs,
    ):
        super().__init__(width=width, height=height, title=title, *args, **kwargs)

        self.context = GLResourceRegistry()
        self.data = data
        self.base_dir = base_dir
        self.glsl_dir = glsl_dir

        self.renderer = ObjectRenderer(
            context=self.context,
            data=self.data,
            base_dir=self.base_dir,
            glsl_dir=self.glsl_dir,
            use_texture=use_texture,
            texture_file=texture_file,
            resource_subdir=resource_subdir,
        )
        self.renderer.show_model = True

    def initialize(self):
        self.initializeGL()
