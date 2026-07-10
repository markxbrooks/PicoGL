from pyglm import glm

Mat4 = glm.mat4


def glm_identity_matrix() -> Mat4:
    return glm.mat4(1.0)
