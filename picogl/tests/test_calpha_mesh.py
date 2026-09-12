"""Tests for :class:`~molib.gl.mesh.calpha.CalphaMeshBuilder`."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from molib.core.constants import MoLibConstant
from molib.gl.mesh.calpha import CalphaMeshBuilder
from picogl.backend.gl.enums import GLDrawMode


def _atom(
    name: str,
    residue_number: int,
    coords: tuple[float, float, float],
    *,
    chain_id: str = "A",
    color: tuple[float, float, float] = (0.2, 0.3, 0.4),
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        chain_id=chain_id,
        coords=np.asarray(coords, dtype=np.float32),
        color=np.asarray(color, dtype=np.float32),
        selected=False,
        parent=SimpleNamespace(residue_number=residue_number, selected=False),
    )


def _chain_color_fn(
    ca_atoms: list[Any],
    chain_colors: dict[str, tuple[float, float, float]],
    chain_id: str,
) -> tuple[np.ndarray, np.ndarray]:
    positions = np.array([atom.coords for atom in ca_atoms], dtype=np.float32)
    base = np.asarray(chain_colors.get(chain_id, (1.0, 0.0, 0.0)), dtype=np.float32)
    colors = np.broadcast_to(base, positions.shape).copy()
    return colors, positions


def _domain_color_fn(
    ca_atoms: list[Any],
    chain_colors: dict[str, tuple[float, float, float]],
    chain_id: str,
) -> tuple[np.ndarray, np.ndarray]:
    del chain_colors, chain_id
    positions = np.array([atom.coords for atom in ca_atoms], dtype=np.float32)
    colors = np.array([atom.color for atom in ca_atoms], dtype=np.float32)
    return colors, positions


def test_calpha_mesh_filters_to_ca_and_sorts_by_residue() -> None:
    atoms = [
        _atom("N", 1, (100.0, 0.0, 0.0)),
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 2, (2.0, 0.0, 0.0)),
        _atom("C", 1, (200.0, 0.0, 0.0)),
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 1, (1.0, 0.0, 0.0)),
    ]
    meshes = CalphaMeshBuilder({"A": (0.8, 0.1, 0.2)}, _chain_color_fn).build(atoms)

    assert set(meshes) == {"A"}
    arrays = meshes["A"]
    np.testing.assert_array_equal(
        arrays.positions,
        np.asarray([(1.0, 0.0, 0.0), (2.0, 0.0, 0.0)], dtype=np.float32),
    )
    np.testing.assert_array_equal(arrays.normals, np.zeros_like(arrays.positions))
    assert arrays.indices is None


def test_calpha_mesh_skips_chain_with_one_ca() -> None:
    atoms = [
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 1, (1.0, 0.0, 0.0), chain_id="A"),
        _atom(
            MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 1, (3.0, 0.0, 0.0), chain_id="B"
        ),
        _atom(
            MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 2, (4.0, 0.0, 0.0), chain_id="B"
        ),
    ]
    meshes = CalphaMeshBuilder(
        {"A": (1.0, 0.0, 0.0), "B": (0.0, 1.0, 0.0)},
        _chain_color_fn,
    ).build(atoms)

    assert set(meshes) == {"B"}
    np.testing.assert_array_equal(
        meshes["B"].positions,
        np.asarray([(3.0, 0.0, 0.0), (4.0, 0.0, 0.0)], dtype=np.float32),
    )


def test_calpha_mesh_chain_mode_broadcasts_chain_colors() -> None:
    atoms = [
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 1, (1.0, 0.0, 0.0)),
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 2, (2.0, 0.0, 0.0)),
    ]
    chain_rgb = (0.8, 0.1, 0.2)
    meshes = CalphaMeshBuilder({"A": chain_rgb}, _chain_color_fn).build(atoms)

    np.testing.assert_array_equal(
        meshes["A"].colors,
        np.asarray([chain_rgb, chain_rgb], dtype=np.float32),
    )


def test_calpha_mesh_domain_mode_uses_atom_color() -> None:
    atoms = [
        _atom(
            MoLibConstant.PEPTIDE_CHAIN_ATOMNAME,
            1,
            (1.0, 0.0, 0.0),
            color=(0.1, 0.2, 0.3),
        ),
        _atom(
            MoLibConstant.PEPTIDE_CHAIN_ATOMNAME,
            2,
            (2.0, 0.0, 0.0),
            color=(0.4, 0.5, 0.6),
        ),
    ]
    meshes = CalphaMeshBuilder({"A": (0.8, 0.1, 0.2)}, _domain_color_fn).build(
        atoms
    )

    np.testing.assert_array_equal(
        meshes["A"].colors,
        np.asarray([(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)], dtype=np.float32),
    )


def test_calpha_mesh_as_meshdata_is_unindexed_line_strip() -> None:
    atoms = [
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 1, (1.0, 0.0, 0.0)),
        _atom(MoLibConstant.PEPTIDE_CHAIN_ATOMNAME, 2, (2.0, 0.0, 0.0)),
    ]
    arrays = CalphaMeshBuilder({"A": (1.0, 0.0, 0.0)}, _chain_color_fn).build(
        atoms
    )["A"]
    mesh = arrays.as_meshdata(mode=GLDrawMode.LINE_STRIP, indexed=False)

    assert mesh.draw_info.mode == GLDrawMode.LINE_STRIP
    assert mesh.draw_info.indexed is False
    assert mesh.indices is None or np.asarray(mesh.indices).size == 0
    np.testing.assert_array_equal(mesh.vertices, arrays.positions)
    np.testing.assert_array_equal(mesh.normals, arrays.normals)
