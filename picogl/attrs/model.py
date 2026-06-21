"""
Ribbon Attributes
"""

from picogl.gpu.buffers.vbo_types import VBOType


class VBOAttrs:
    """VBO Attrs"""

    VBO = VBOType.VBO
    NBO = VBOType.NBO
    CBO = VBOType.CBO
    EBO = VBOType.EBO
    ALL = [VBOType.VBO, VBOType.NBO, VBOType.CBO, VBOType.EBO]
