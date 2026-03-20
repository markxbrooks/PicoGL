from enum import Enum


class ShaderType(str, Enum):
    """Shader Type"""
    AXIS = "axis"
    ATOMS = "atoms"
    BONDS = "bonds"
    CALPHAS = "calphas"
    DEFAULT = "default"
    ISOSURFACE = "isosurface"
    MESH = "mesh"
    RIBBONS = "ribbons"
    SURFACE_WITH_LIGHTING = "surface_with_lighting"
    SURFACE_BASIC = "surface_basic"
    TEXTURED_CUBE = "textured_cube"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def get_name(self):
        return self.value

    def get_display_name(self):
        return self.value + "_shader"

    def vertex_path(self):
        return f"{self.value}_vert.glsl"

    def fragment_path(self):
        return f"{self.value}_frag.glsl"
