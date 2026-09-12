"""CPU-side mesh arrays used by geometry builders."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from picogl.backend.gl.enums import GLDrawMode
from picogl.renderer.draw_spec import MeshDrawInfo
from picogl.renderer.meshdata import MeshData


@dataclass(frozen=True, slots=True)
class MeshArrays:
    """Immutable NumPy arrays for positions, normals, colors, and indices.

    Geometry producers return this type. Color is optional: atom/bond
    geometry typically omits it, and :class:`~picogl.renderer.molecular.atoms.AtomsMesh`
    / :class:`~picogl.renderer.molecular.bonds.BondsMesh` attach it later.
    Primitive mode is not stored here; :meth:`as_meshdata` supplies
    :class:`~picogl.renderer.draw_spec.MeshDrawInfo`.
    """

    positions: np.ndarray
    normals: np.ndarray
    colors: np.ndarray | None = None
    indices: np.ndarray | None = None

    def __post_init__(self) -> None:
        positions = np.asarray(self.positions, dtype=np.float32)
        normals = np.asarray(self.normals, dtype=np.float32)

        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError("positions must have shape (N, 3)")

        if normals.shape != positions.shape:
            raise ValueError("normals must have shape (N, 3)")

        colors = None
        if self.colors is not None:
            colors = np.asarray(self.colors, dtype=np.float32)
            if colors.shape == (3,):
                colors = np.broadcast_to(colors, positions.shape).copy()
            elif colors.shape != positions.shape:
                raise ValueError("colors must have shape (3,) or (N, 3)")

        indices = None
        if self.indices is not None:
            indices = np.asarray(self.indices, dtype=np.uint32)
            if indices.ndim != 1:
                raise ValueError("indices must have shape (M,)")
            n_vertices = int(positions.shape[0])
            if indices.size and np.any(indices >= n_vertices):
                raise ValueError("indices contain out-of-range vertex references")

        object.__setattr__(self, "positions", positions)
        object.__setattr__(self, "normals", normals)
        object.__setattr__(self, "colors", colors)
        object.__setattr__(self, "indices", indices)

    @property
    def indexed(self) -> bool:
        """Whether this mesh carries an index buffer."""
        return self.indices is not None

    def with_colors(self, colors: np.ndarray) -> MeshArrays:
        """Return a copy with *colors* replacing the current color array.

        Parameters
        ----------
        colors
            RGB triples with shape ``(3,)`` or ``(N, 3)``.

        Returns
        -------
        MeshArrays
            New value with the same positions, normals, and indices.
        """
        return replace(self, colors=colors)

    def as_meshdata(
        self,
        *,
        mode: GLDrawMode = GLDrawMode.TRIANGLES,
    ) -> MeshData:
        """Convert these arrays into renderable :class:`~picogl.renderer.meshdata.MeshData`.

        Parameters
        ----------
        mode
            Primitive mode. Defaults to triangles so unindexed geometry is
            not inferred as points.

        Returns
        -------
        MeshData
            CPU mesh with ``draw_info`` derived from *mode* and :attr:`indexed`.
        """
        return MeshData(
            vertices=self.positions,
            normals=self.normals,
            colors=self.colors,
            indices=self.indices,
            draw_info=MeshDrawInfo(mode=mode, indexed=self.indexed),
        )
