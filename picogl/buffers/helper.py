from typing import Any

import numpy as np
from numpy import ndarray, dtype, generic


def as_vec3_array(data) -> ndarray[Any, dtype[generic]]:
    """as vec3 array"""
    return np.asarray(data, dtype=np.float32).reshape(-1, 3)
