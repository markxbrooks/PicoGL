from picogl.utils.strenum import StrEnum


class VBOType(StrEnum):
    """VBO Type"""

    VBO = "vbo"
    CBO = "cbo"
    NBO = "nbo"
    EBO = "ebo"
    UVS = "uvs"

class VBODataType(StrEnum):
    """VBO Type"""

    VBO = "vertices"
    CBO = "colors"
    NBO = "normals"
    EBO = "indices"
    UVS = "texcoords"


ATTRIBUTE_LAYOUT = {
    VBOType.VBO: 3,
    VBOType.NBO: 3,
    VBOType.CBO: None,  # dynamic
}

def get_stride(attr, data):
    if ATTRIBUTE_LAYOUT[attr] is not None:
        return ATTRIBUTE_LAYOUT[attr]
    return data.shape[1]
