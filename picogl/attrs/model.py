"""
Ribbon Attributes
"""

from picogl.buffers.vertex.vbo.vbo_class import VBOType


class VBOAttrs:
    """VBO Attrs"""

    VBO = VBOType.VBO
    NBO = VBOType.NBO
    CBO = VBOType.CBO
    EBO = VBOType.EBO
    ALL = [VBOType.VBO, VBOType.NBO, VBOType.CBO, VBOType.EBO]
