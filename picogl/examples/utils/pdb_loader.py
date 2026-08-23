"""
PDB File Loader for MolViewSpec Integration

This module provides functionality to:
1. Load and parse PDB files
2. Convert PDB data to MolViewSpec format
3. Integrate with PicoGL's molecular visualization system
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from molib.ligand.pdb.layouts.pdb_file import PDBFileLayout, PDBTitleLayout

from utils.bond_detection import atoms_should_bond


@dataclass
class Atom:
    """Represents a single atom from a PDB file"""

    serial: int
    name: str
    res_name: str
    chain_id: str
    res_seq: int
    x: float
    y: float
    z: float
    element: str
    charge: str = ""
    occupancy: float = 1.0
    b_factor: float = 0.0


class BondType:
    SINGLE: str = "single"
    DOUBLE: str = "double"
    TRIPLE: str = "triple"
    AROMATIC: str = "aromatic"


@dataclass
class Bond:
    """Represents a bond between two atoms"""

    atom1_idx: int
    atom2_idx: int
    bond_type: BondType = BondType.SINGLE


@dataclass
class Residue:
    """Represents a residue/amino acid"""

    name: str
    chain_id: str
    seq_num: int
    atoms: List[Atom]
    start_idx: int  # Index in the main atom list


@dataclass
class PDBStructure:
    """Complete PDB structure data"""

    title: str
    atoms: List[Atom]
    bonds: List[Bond]
    residues: List[Residue]
    chains: List[str]

    def get_atom_positions(self) -> np.ndarray:
        """Get all atom positions as a numpy array"""
        return np.array(
            [[atom.x, atom.y, atom.z] for atom in self.atoms], dtype=np.float32
        )

    def get_atom_elements(self) -> List[str]:
        """Get all atom element symbols"""
        return [atom.element for atom in self.atoms]

    def get_residue_atoms(self, residue_idx: int) -> List[Atom]:
        """Get atoms for a specific residue"""
        if 0 <= residue_idx < len(self.residues):
            return self.residues[residue_idx].atoms
        return []


def _pdb_line(raw_line: str) -> str:
    """Normalize a PDB text line for fixed-width field parsing."""
    line = raw_line.rstrip("\n\r")
    if len(line) < 80:
        line = line.ljust(80)
    return line


def _optional_float(value, default: float) -> float:
    if value == "" or value is None:
        return default
    return float(value)


def _parse_atom_line(line: str) -> Atom:
    """Parse an ATOM or HETATM line from PDB format."""
    layout = PDBFileLayout
    return Atom(
        serial=layout.atom_serial.parse(line),
        name=layout.atom_name.parse(line),
        res_name=layout.res_name.parse(line),
        chain_id=layout.chain_id.parse(line),
        res_seq=layout.res_seq.parse(line),
        x=layout.x.parse(line),
        y=layout.y.parse(line),
        z=layout.z.parse(line),
        element=layout.element.parse(line),
        occupancy=_optional_float(layout.occupancy.parse(line), 1.0),
        b_factor=_optional_float(layout.temp_factor.parse(line), 0.0),
    )


def _bond_key(i: int, j: int) -> tuple[int, int]:
    return (i, j) if i < j else (j, i)


def _atom_distance(a: Atom, b: Atom) -> float:
    return float(
        np.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
    )


def _parse_conect_line(
    line: str, serial_to_idx: Dict[int, int]
) -> List[Bond]:
    """Parse a CONECT line into bonds (central atom → up to four partners)."""
    bonds: List[Bond] = []
    try:
        # Columns 7-11 central; 12-16, 17-21, 22-26, 27-31 bonded serials.
        fields = [line[i : i + 5] for i in range(6, 31, 5)]
        serials = []
        for field in fields:
            text = field.strip()
            if text:
                serials.append(int(text))
        if len(serials) < 2:
            return bonds
        center = serial_to_idx.get(serials[0])
        if center is None:
            return bonds
        for partner_serial in serials[1:]:
            partner = serial_to_idx.get(partner_serial)
            if partner is not None and partner != center:
                bonds.append(
                    Bond(
                        atom1_idx=center,
                        atom2_idx=partner,
                        bond_type=BondType.SINGLE,
                    )
                )
    except (ValueError, IndexError, TypeError):
        pass
    return bonds


def _find_named_atom(residue: Residue, name: str) -> Optional[Atom]:
    for atom in residue.atoms:
        if atom.name.strip() == name:
            return atom
    return None


def _generate_bonds(atoms: List[Atom], residues: List[Residue]) -> List[Bond]:
    """Infer covalent bonds from geometry (protein/ligand sticks).

    PDB ``CONECT`` records usually cover ligands only. Protein connectivity
    must be rebuilt from residue geometry.
    """
    bonds: List[Bond] = []
    atom_index = {id(atom): i for i, atom in enumerate(atoms)}

    # Intra-residue bonds from distance + element heuristics.
    for residue in residues:
        res_atoms = residue.atoms
        for i in range(len(res_atoms)):
            for j in range(i + 1, len(res_atoms)):
                atom1 = res_atoms[i]
                atom2 = res_atoms[j]
                dist = _atom_distance(atom1, atom2)
                if atoms_should_bond(atom1, atom2, dist):
                    bonds.append(
                        Bond(
                            atom1_idx=atom_index[id(atom1)],
                            atom2_idx=atom_index[id(atom2)],
                            bond_type=BondType.SINGLE,
                        )
                    )

    # Peptide bonds: carbonyl C of residue i to amide N of residue i+1.
    for i in range(len(residues) - 1):
        curr_res = residues[i]
        next_res = residues[i + 1]
        if (
            curr_res.chain_id != next_res.chain_id
            or next_res.seq_num != curr_res.seq_num + 1
        ):
            continue
        carbon = _find_named_atom(curr_res, "C")
        nitrogen = _find_named_atom(next_res, "N")
        if carbon is None or nitrogen is None:
            continue
        dist = _atom_distance(carbon, nitrogen)
        if dist <= 2.0:  # typical peptide bond ~1.33 Å
            bonds.append(
                Bond(
                    atom1_idx=atom_index[id(carbon)],
                    atom2_idx=atom_index[id(nitrogen)],
                    bond_type=BondType.SINGLE,
                )
            )

    return bonds


def _merge_bonds(*bond_lists: List[Bond]) -> List[Bond]:
    """Union bond lists, dropping duplicate undirected pairs."""
    seen: set[tuple[int, int]] = set()
    merged: List[Bond] = []
    for bond_list in bond_lists:
        for bond in bond_list:
            key = _bond_key(bond.atom1_idx, bond.atom2_idx)
            if key in seen:
                continue
            seen.add(key)
            merged.append(bond)
    return merged


class PDBLoader:
    """Loads and parses PDB files"""

    def __init__(self, path: str):
        # Resolve the path
        if not os.path.isabs(path):
            if os.path.exists(path):
                path = os.path.abspath(path)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.abspath(os.path.join(script_dir, "..", path))

        if not os.path.exists(path):
            raise FileNotFoundError(f"PDB file not found: {path}")

        self.path = path
        self.structure = None
        self._load_pdb()

    def _load_pdb(self):
        """Load and parse the PDB file"""
        atoms, conect_bonds, chains, current_residue, current_residue_atoms, residues, title = self.open_file()

        # Add the last residue
        if current_residue is not None:
            current_residue.atoms = current_residue_atoms
            residues.append(current_residue)

        # CONECT usually lists ligands only; always infer protein/ligand sticks
        # from geometry and merge with any explicit CONECT pairs.
        inferred = _generate_bonds(atoms, residues)
        bonds = _merge_bonds(conect_bonds, inferred)

        self.structure = PDBStructure(
            title=title,
            atoms=atoms,
            bonds=bonds,
            residues=residues,
            chains=list(chains),
        )

    def open_file(self) -> tuple[list[Atom], list[Any], list[Any], list[Any], list[Atom], list[Residue], str]:
        atoms: list[Atom] = []
        bonds = []
        residues = []
        chains = set()
        title = "Unknown Structure"

        current_residue = None
        current_residue_atoms = []

        with open(self.path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = _pdb_line(raw_line)
                if not line.strip():
                    continue

                record_type = PDBFileLayout.record_type.parse(line)

                if record_type == "TITLE":
                    title = PDBTitleLayout.title.parse(line) or title

                elif record_type in ("ATOM", "HETATM"):
                    atom = _parse_atom_line(line)
                    atoms.append(atom)
                    chains.add(atom.chain_id)

                    # Group atoms by residue
                    if (
                            current_residue is None
                            or current_residue.name != atom.res_name
                            or current_residue.chain_id != atom.chain_id
                            or current_residue.seq_num != atom.res_seq
                    ):
                        # Save previous residue
                        if current_residue is not None:
                            current_residue.atoms = current_residue_atoms
                            residues.append(current_residue)

                        # Start new residue
                        current_residue = Residue(
                            name=atom.res_name,
                            chain_id=atom.chain_id,
                            seq_num=atom.res_seq,
                            atoms=[],
                            start_idx=len(atoms) - 1,
                        )
                        current_residue_atoms = []

                    current_residue_atoms.append(atom)

                elif record_type == "CONECT":
                    # Serial→index map once atoms are complete; CONECT is at EOF.
                    if not hasattr(self, "_serial_to_idx") or len(
                        getattr(self, "_serial_to_idx", {})
                    ) != len(atoms):
                        self._serial_to_idx = {
                            atom.serial: i for i, atom in enumerate(atoms)
                        }
                    bonds.extend(
                        _parse_conect_line(line, self._serial_to_idx)
                    )

                elif record_type == "END":
                    break
        return atoms, bonds, chains, current_residue, current_residue_atoms, residues, title

    def to_molviewspec(self) -> Dict:
        """Convert PDB structure to MolViewSpec format"""
        if not self.structure:
            raise ValueError("No structure loaded")

        # Create MolViewSpec representation
        molviewspec = {
            "version": "1.0.0",
            "name": self.structure.title,
            "description": f"PDB structure loaded from {os.path.basename(self.path)}",
            "camera": {"position": [0, 0, 50], "target": [0, 0, 0], "up": [0, 1, 0]},
            "components": [],
        }

        # Add atoms as spheres
        atom_component = {
            "type": "representation",
            "kind": "ball-and-stick",
            "props": {"alpha": 1.0, "colour": "element-symbol"},
            "data": {
                "x": [atom.x for atom in self.structure.atoms],
                "y": [atom.y for atom in self.structure.atoms],
                "z": [atom.z for atom in self.structure.atoms],
                "element": [atom.element for atom in self.structure.atoms],
                "residue_name": [atom.res_name for atom in self.structure.atoms],
                "residue_seq": [atom.res_seq for atom in self.structure.atoms],
                "chain_id": [atom.chain_id for atom in self.structure.atoms],
            },
        }
        molviewspec["components"].append(atom_component)

        # Add bonds as cylinders
        if self.structure.bonds:
            bond_component = {
                "type": "representation",
                "kind": "line",
                "props": {"alpha": 1.0, "colour": "element-symbol"},
                "data": {
                    "positionA": [
                        [
                            self.structure.atoms[bond.atom1_idx].x,
                            self.structure.atoms[bond.atom1_idx].y,
                            self.structure.atoms[bond.atom1_idx].z,
                        ]
                        for bond in self.structure.bonds
                    ],
                    "positionB": [
                        [
                            self.structure.atoms[bond.atom2_idx].x,
                            self.structure.atoms[bond.atom2_idx].y,
                            self.structure.atoms[bond.atom2_idx].z,
                        ]
                        for bond in self.structure.bonds
                    ],
                },
            }
            molviewspec["components"].append(bond_component)

        return molviewspec

    def to_picogl_data(self) -> Dict:
        """Convert PDB structure to PicoGL-compatible data format"""
        if not self.structure:
            raise ValueError("No structure loaded")

        # Get atom positions
        positions = self.structure.get_atom_positions()
        elements = self.structure.get_atom_elements()

        # Generate colors based on element types
        element_colors = {
            "C": [0.2, 0.2, 0.2],  # Dark gray
            "N": [0.0, 0.0, 1.0],  # Blue
            "O": [1.0, 0.0, 0.0],  # Red
            "S": [1.0, 1.0, 0.0],  # Yellow
            "P": [1.0, 0.5, 0.0],  # Orange
            "H": [1.0, 1.0, 1.0],  # White
        }

        colors = []
        for element in elements:
            colors.extend(element_colors.get(element, [0.5, 0.5, 0.5]))

        # Generate bond data
        bond_positions = []
        bond_colors = []

        for bond in self.structure.bonds:
            atom1 = self.structure.atoms[bond.atom1_idx]
            atom2 = self.structure.atoms[bond.atom2_idx]

            # Bond colour (average of the two atom colors)
            color1 = element_colors.get(atom1.element, [0.5, 0.5, 0.5])
            color2 = element_colors.get(atom2.element, [0.5, 0.5, 0.5])
            bond_color = [(c1 + c2) / 2 for c1, c2 in zip(color1, color2)]

            # Add bond vertices (two points for each bond)
            bond_positions.extend([atom1.x, atom1.y, atom1.z])
            bond_positions.extend([atom2.x, atom2.y, atom2.z])
            bond_colors.extend(bond_color * 2)  # Color for both vertices

        return {
            "atoms": {
                "positions": positions.flatten().tolist(),
                "colors": colors,
                "elements": elements,
                "count": len(self.structure.atoms),
            },
            "bonds": {
                "positions": bond_positions,
                "colors": bond_colors,
                "count": len(self.structure.bonds),
            },
            "residues": [res.name for res in self.structure.residues],
            "chains": self.structure.chains,
        }


def save_molviewspec(molviewspec: Dict, output_path: str):
    """Save MolViewSpec data to a JSON file"""
    import json

    with open(output_path, "w") as f:
        json.dump(molviewspec, f, indent=2)


if __name__ == "__main__":
    # Example usage
    try:
        # Load a PDB file
        loader = PDBLoader("data/example.pdb")

        print(f"Loaded structure: {loader.structure.title}")
        print(f"Atoms: {len(loader.structure.atoms)}")
        print(f"Bonds: {len(loader.structure.bonds)}")
        print(f"Residues: {len(loader.structure.residues)}")
        print(f"Chains: {loader.structure.chains}")

        # Convert to MolViewSpec
        molviewspec = loader.to_molviewspec()
        save_molviewspec(molviewspec, "output.molviewspec")
        print("Saved MolViewSpec file: output.molviewspec")

        # Convert to PicoGL data
        picogl_data = loader.to_picogl_data()
        print(
            f"PicoGL data: {picogl_data['atoms']['count']} atoms, {picogl_data['bonds']['count']} bonds"
        )

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you have a PDB file in the data/ directory")
    except Exception as e:
        print(f"Error: {e}")
