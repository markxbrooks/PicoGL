"""Tests for PDBLoaderResults typed parse output."""

from __future__ import annotations

import os
import sys

import pytest

_EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
_UTILS_DIR = os.path.join(_EXAMPLES_DIR, "utils")
if _EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, _EXAMPLES_DIR)
if _UTILS_DIR not in sys.path:
    sys.path.insert(0, _UTILS_DIR)

from pdb_loader import PDBLoader, PDBLoaderResults  # noqa: E402

_PDB_FIXTURE = os.path.abspath(
    os.path.join(
        _EXAMPLES_DIR, "..", "..", "..", "ElMo", "elmo", "test_data", "2VUG.pdb"
    )
)


@pytest.fixture
def pdb_path() -> str:
    if not os.path.isfile(_PDB_FIXTURE):
        pytest.skip(f"PDB fixture not found: {_PDB_FIXTURE}")
    return _PDB_FIXTURE


def test_open_file_returns_pdb_loader_results(pdb_path: str) -> None:
    loader = PDBLoader(pdb_path)
    results = loader.open_file()

    assert isinstance(results, PDBLoaderResults)
    assert len(results.atoms) > 0
    assert isinstance(results.chains, set)
    assert results.title


def test_to_structure_matches_loader_structure(pdb_path: str) -> None:
    loader = PDBLoader(pdb_path)
    results = loader.open_file()
    structure = results.to_structure()

    assert len(structure.atoms) == len(loader.structure.atoms)
    assert len(structure.residues) == len(loader.structure.residues)
    assert len(structure.bonds) == len(loader.structure.bonds)
    assert structure.title == loader.structure.title
    assert structure.chains == loader.structure.chains


def test_inferred_bonds_added_beyond_conect(pdb_path: str) -> None:
    loader = PDBLoader(pdb_path)
    results = loader.open_file()
    structure = results.to_structure()

    assert len(structure.bonds) >= len(results.conect_bonds)
