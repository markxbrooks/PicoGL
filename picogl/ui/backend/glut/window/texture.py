from pathlib import Path

from picogl.renderer import GLContext, MeshData
from picogl.renderer.texture import TextureRenderer
from picogl.ui.backend.glut.window.glut import GlutRendererWindow


class TextureWindow(GlutRendererWindow):
    """file with stubs for actions"""

    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        data: MeshData,
        base_dir: str | Path,
        glsl_dir: str | Path,
        use_texture: bool,
        *args,
        **kwargs,
    ):
        self.context = GLContext()
        self.base_dir = base_dir
        self.data = data
        super().__init__(
            width, height, title, data=self.data, context=self.context, *args, **kwargs
        )
        self.renderer = TextureRenderer(
            context=self.context,
            data=self.data,
            base_dir=self.base_dir,
            glsl_dir=glsl_dir,
            use_texture=use_texture,
        )
