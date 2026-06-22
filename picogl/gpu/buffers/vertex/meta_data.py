from typing import Optional

import numpy as np


class VertexMetadata:
    """CPU side vertex data."""

    __slots__ = ("chain_ids", "secondary_structure")

    def __init__(
        self,
        chain_ids: Optional[list[str]] = None,
        secondary_structure: Optional[np.ndarray] = None,
    ):
        self.chain_ids = chain_ids
        self.secondary_structure = secondary_structure
