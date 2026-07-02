"""
Provides the TextureRenderer class for rendering textured objects.

This module includes the implementation for the TextureRenderer,
which is responsible for handling rendering operations involving
mesh data and texture loading.
"""

from pathlib import Path

from picogl.renderer import GLResourceRegistry, MeshData
from picogl.renderer.object import ObjectRenderer
from picogl.utils.loader.texture import TextureLoader


class TextureRenderer(ObjectRenderer):
    """Basic renderer class"""

    def __init__(
        self,
        context: GLResourceRegistry,
        data: MeshData,
        base_dir: str | Path = None,
        glsl_dir: str | Path = None,
        use_texture: bool = False,
        texture_file: str = None,
        resource_subdir: str = None,
    ):
        super().__init__(
            context=context,
            data=data,
            base_dir=base_dir,
            glsl_dir=glsl_dir,
            use_texture=use_texture,
        )
        self.texture_full_path = None
        self.resource_full_path = None
        self.texture = None
        self.context = context
        self.data = data
        self.data.vertex_count = len(self.data.vertices.flatten()) // 3
        self.show_model = True
        self.base_dir = base_dir
        self.base_path = Path(base_dir) if base_dir is not None else Path(".")
        self.glsl_dir = glsl_dir

        self.initialize_textures()

    def initialize_textures(self):
        # Build paths
        texture_path = self.get_texture_filename()
        self.texture = texture = TextureLoader(texture_path)
        self.context.texture_id = texture.texture_gl_id
        if texture.inversed_v_coords:
            for index, _ in enumerate(self.data.texcoords):
                if index % 2:
                    self.data.texcoords[index] = 1.0 - self.data.texcoords[index]

    def get_texture_filename(self):
        """
        get texture filename

        :return: texture filename: str
        """
        self.set_resource_path(self.base_path, "tu02")
        self.set_texture_filename("uvtemplate.tga")
        texture_path = str(self.texture_full_path)
        return texture_path

    def set_texture_filename(self, file_name: str = None):
        """
        set_texture_filename

        :param file_name: str = None
        :return: None
        """
        if file_name is not None:
            self.texture_full_path = self.resource_full_path / file_name
        else:
            self.texture_full_path = self.resource_full_path / "default_texture.tga"

    def set_resource_path(self, base_path: str | Path, subdir: str):
        """
        set_resource_path

        :param base_path: str | Path
        :param subdir: str
        """
        base_path_obj = Path(base_path) if isinstance(base_path, str) else base_path
        self.resource_full_path = base_path_obj.absolute() / "resources" / subdir

    def _draw_selection(self):
        """Draw selection"""
