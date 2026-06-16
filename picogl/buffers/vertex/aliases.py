from enum import Enum

from picogl.buffers.vertex.vbo.vbo_class import VBOType


class VertexBufferRole(str, Enum):
    """Enum for vertex buffer types."""

    VBO = VBOType.VBO
    CBO = VBOType.CBO
    NBO = VBOType.NBO
    EBO = VBOType.EBO


class VertexArrayRole(str, Enum):
    """Enum for vertex array types."""

    VAO = "handle"
    named_vbos: dict[VertexBufferRole, int]


NAME_ALIASES = {
    "positions": VertexBufferRole.VBO,
    VBOType.VBO: VertexBufferRole.VBO,
    "colors": VertexBufferRole.CBO,
    VBOType.CBO: VertexBufferRole.CBO,
    "normals": VertexBufferRole.NBO,
    VBOType.NBO: VertexBufferRole.NBO,
    "indices": VertexBufferRole.EBO,
    VBOType.EBO: VertexBufferRole.EBO,
    "elements": VertexBufferRole.EBO,
}

__all__ = ["VertexBufferRole", "NAME_ALIASES"]
