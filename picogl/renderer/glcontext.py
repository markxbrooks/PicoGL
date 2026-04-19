"""
GL Context Class
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.shaders import ShaderType


@dataclass
class GLContext:
    vaos: dict[str, VertexArrayObject] = field(default_factory=dict)
    current_vao: Optional[VertexArrayObject] = None

    shader_type: ShaderType = ShaderType.DEFAULT

    textures: dict[str, int] = field(default_factory=dict)
    active_texture: Optional[str] = None

    model_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))
    view_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))
    projection_matrix: np.ndarray = field(default_factory=lambda: np.identity(4, dtype=np.float32))

    eye_position: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=np.float32))
