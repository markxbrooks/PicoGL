from enum import Enum


class VertexBufferRole(str, Enum):
    """Enum for vertex buffer types."""
    VBO = "vbo"
    CBO = "cbo"
    NBO = "nbo"
    EBO = "ebo"


class VertexArrayRole(str, Enum):
    """Enum for vertex array types."""
    VAO = "handle"
    named_vbos: dict[VertexBufferRole, int]


NAME_ALIASES = {
    "positions": VertexBufferRole.VBO,
    "vbo": VertexBufferRole.VBO,
    "colors": VertexBufferRole.CBO,
    "cbo": VertexBufferRole.CBO,
    "normals": VertexBufferRole.NBO,
    "nbo": VertexBufferRole.NBO,
    "indices": VertexBufferRole.EBO,
    "ebo": VertexBufferRole.EBO,
    "elements": VertexBufferRole.EBO,
}

__all__ = ["VertexBufferRole", "NAME_ALIASES"]