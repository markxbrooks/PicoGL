"""
Represents a rectangular viewport with position and dimensions.

The class provides positional information, size, aspect ratio, and a method
to retrieve the viewport as a numerical array.

"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy import dtype, generic, ndarray
from pyglm import glm


@dataclass(frozen=True, slots=True)
class Viewport:
    """Represents a rectangular viewport with position and dimensions."""

    x: int
    y: int
    width: int
    height: int

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height else 1.0

    def as_array(self) -> np.ndarray:
        return np.array(
            [self.x, self.y, self.width, self.height],
            dtype=np.int32,
        )

    def as_tuple(self) -> tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height

    def unproject(
        self, x: float, y: float, depth: float, inv_mvp: glm.mat4
    ) -> np.ndarray | None:
        """unproject"""

        y = self.flip_y(y)

        ndc = self.ndc(depth, x, y)

        world = self.world(inv_mvp, ndc)

        w = world[3]
        if abs(w) < 1e-8:
            return None

        world = world / w
        return world[:3]

    def flip_y(self, y: float) -> float:
        y = self.height - y
        return y

    @staticmethod
    def world(inv_mvp: glm.mat4, ndc: np.ndarray) -> np.ndarray:
        return np.asarray(inv_mvp @ ndc, dtype=np.float32)

    def ndc(
        self, depth: float, x: float, y: float
    ) -> ndarray[Any, dtype[Any]] | ndarray[Any, dtype[generic]]:
        ndc = np.array(
            [
                (x - self.x) / self.width * 2.0 - 1.0,
                (y - self.y) / self.height * 2.0 - 1.0,
                depth * 2.0 - 1.0,
                1.0,
            ],
            dtype=np.float32,
        )
        return ndc

    def _unproject_for_depth(
        self, x: float, y: float, inv_mvp, depth: float
    ) -> ndarray | None:
        return self.unproject(float(x), float(y), depth, inv_mvp)

    def near(self, x: float, y: float, inv_mvp: glm.mat4) -> ndarray | None:
        return self._unproject_for_depth(x=x, y=y, inv_mvp=inv_mvp, depth=0.0)

    def far(self, x: float, y: float, inv_mvp: glm.mat4) -> ndarray | None:
        return self._unproject_for_depth(x=x, y=y, inv_mvp=inv_mvp, depth=1.0)

    @property
    def center(self) -> tuple[float, float]:
        return (
            self.x + self.width / 2,
            self.y + self.height / 2,
        )

    def contains(self, x: float, y: float) -> bool:
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (
            self.x,
            self.y,
            self.width,
            self.height,
        )
