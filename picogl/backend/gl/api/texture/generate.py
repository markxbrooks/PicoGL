from __future__ import annotations

import numpy as np
from OpenGL.GL import glGenTextures


def gl_gen_textures(number: int = 1) -> int:
    """Issue ``glGenTextures``."""
    result = glGenTextures(number)
    if number == 1:
        if hasattr(result, "__len__") and not isinstance(result, (int, np.integer)):
            return int(result[0])
        return int(result)
    return result
