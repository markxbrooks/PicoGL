import numpy as np


def compute_vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """
    vertices: (N, 3)
    faces:    (M, 3)  0-based indices
    returns:  (N, 3) normalized vertex normals
    """
    normals = np.zeros_like(vertices, dtype=np.float32)
    # gather vertices per triangle
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]

    face_normals = np.cross(v1 - v0, v2 - v0)
    # accumulate
    for i in range(3):
        np.add.at(normals, faces[:, i], face_normals)

    # normalize
    lengths = np.linalg.norm(normals, axis=1)
    normals[lengths > 0] /= lengths[lengths > 0][:, None]
    return normals
