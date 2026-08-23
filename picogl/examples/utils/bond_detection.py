"""Lightweight covalent bond heuristics for PDB examples (no ElMo / Qt deps)."""

from __future__ import annotations

from typing import Any

BOND_LENGTHS_SIMPLE: dict[tuple[str, str], float] = {
    ("C", "C"): 1.53,
    ("C", "N"): 1.47,
    ("C", "O"): 1.43,
    ("C", "S"): 1.82,
    ("N", "N"): 1.45,
    ("N", "O"): 1.36,
    ("O", "O"): 1.48,
    ("S", "S"): 2.05,
    ("C", "H"): 1.059,
    ("C", "F"): 1.34,
    ("C", "CL"): 1.734,
    ("N", "H"): 1.01,
    ("O", "H"): 0.96,
    ("S", "H"): 1.34,
}

BIO_ELEMENTS = {"C", "N", "O", "S", "P"}
METALS = {"FE", "ZN", "CA", "MG", "MN", "CU"}
HALOGENS = {"F", "CL", "BR", "I"}


def _normalize_elements(atom1: Any, atom2: Any) -> tuple[str, str] | None:
    e1 = getattr(atom1, "element", None)
    e2 = getattr(atom2, "element", None)
    if not e1 or not e2:
        return None
    return e1.upper().strip(), e2.upper().strip()


def _within_tolerance(distance: float, expected: float, tol: float = 0.25) -> bool:
    return distance <= expected * (1 + tol)


def atoms_should_bond(atom1: Any, atom2: Any, distance: float) -> bool:
    """Return True when *distance* is consistent with a covalent bond between *atom1* and *atom2*."""
    elements = _normalize_elements(atom1, atom2)
    if elements is None:
        return False

    e1, e2 = elements
    key = tuple(sorted(elements))

    if key in BOND_LENGTHS_SIMPLE:
        return _within_tolerance(distance, BOND_LENGTHS_SIMPLE[key])

    if "H" in elements:
        return distance <= 1.1

    if e1 in METALS or e2 in METALS:
        return distance <= 3.0

    if (e1 in HALOGENS or e2 in HALOGENS) and (
        e1 in BIO_ELEMENTS or e2 in BIO_ELEMENTS
    ):
        return distance <= 2.5

    if e1 in BIO_ELEMENTS and e2 in BIO_ELEMENTS:
        return distance <= 2.2

    return False
