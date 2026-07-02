"""
PDB File Loader for MolViewSpec Integration

This module provides functionality to:
1. Load and parse PDB files
2. Convert PDB data to MolViewSpec format
3. Integrate with PicoGL's molecular visualization system
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from elmo.gl.backend.modern.entities.bonds.compute_indices import \
    atoms_should_bond


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

"""
def atoms_should_bond(atom1: Atom, atom2: Atom, distance: float) -> bool:
    ""Determine if two atoms should be bonded based on distance and element types""
    # Common covalent bond lengths (in Angstroms)
    bond_lengths = {
        ("C", "C"): 1.54,
        ("C", "N"): 1.47,
        ("C", "O"): 1.43,
        ("C", "S"): 1.82,
        ("N", "N"): 1.45,
        ("N", "O"): 1.36,
        ("O", "O"): 1.48,
        ("S", "S"): 2.05,
    }

    # Check if we have a known bond length
    key = tuple(sorted([atom1.element, atom2.element]))
    if key in bond_lengths:
        expected_length = bond_lengths[key]
        # Allow some tolerance (20%)
        return distance <= expected_length * 1.2

    # Fallback: use a general rule based on element types
    if atom1.element in ["C", "N", "O", "S"] and atom2.element in ["C", "N", "O", "S"]:
        return distance <= 2.0

    return False"""


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
        atoms = []
        bonds = []
        residues = []
        chains = set()
        title = "Unknown Structure"

        current_residue = None
        current_residue_atoms = []

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                record_type = line[:6].strip()

                if record_type == "TITLE":
                    title = line[10:].strip()

                elif record_type == "ATOM" or record_type == "HETATM":
                    atom = self._parse_atom_line(line)
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
                    bond = self._parse_conect_line(line, atoms)
                    if bond:
                        bonds.append(bond)

                elif record_type == "END":
                    break

        # Add the last residue
        if current_residue is not None:
            current_residue.atoms = current_residue_atoms
            residues.append(current_residue)

        # Generate missing bonds based on distance and residue connectivity
        if not bonds:
            bonds = self._generate_bonds(atoms, residues)

        self.structure = PDBStructure(
            title=title,
            atoms=atoms,
            bonds=bonds,
            residues=residues,
            chains=list(chains),
        )

    def _parse_atom_line(self, line: str) -> Atom:
        """Parse an ATOM or HETATM line from PDB format"""
        return Atom(
            serial=int(line[6:11]),
            name=line[12:16].strip(),
            res_name=line[17:20].strip(),
            chain_id=line[21:22].strip(),
            res_seq=int(line[22:26]),
            x=float(line[30:38]),
            y=float(line[38:46]),
            z=float(line[46:54]),
            element=line[76:78].strip(),
            occupancy=float(line[54:60]) if line[54:60].strip() else 1.0,
            b_factor=float(line[60:66]) if line[60:66].strip() else 0.0,
        )

    def _parse_conect_line(self, line: str, atoms: List[Atom]) -> Optional[Bond]:
        """Parse a CONECT line to extract bond information"""
        try:
            atom1_idx = int(line[6:11]) - 1  # Convert to 0-based index
            atom2_idx = int(line[11:16]) - 1

            if 0 <= atom1_idx < len(atoms) and 0 <= atom2_idx < len(atoms):
                return Bond(atom1_idx=atom1_idx, atom2_idx=atom2_idx)
        except (ValueError, IndexError):
            pass
        return None

    def _generate_bonds(self, atoms: List[Atom], residues: List[Residue]) -> List[Bond]:
        """Generate bonds based on residue connectivity and distance"""
        bonds = []

        # Add peptide bonds between consecutive residues
        for i in range(len(residues) - 1):
            curr_res = residues[i]
            next_res = residues[i + 1]

            if (
                curr_res.chain_id == next_res.chain_id
                and next_res.seq_num == curr_res.seq_num + 1
            ):
                # Find C-alpha atoms
                ca1 = None
                ca2 = None

                for atom in curr_res.atoms:
                    if atom.name.strip() == MoLibConstant.PEPTIDE_CHAIN_ATOMNAME:
                        ca1 = atom
                        break

                for atom in next_res.atoms:
                    if atom.name.strip() == MoLibConstant.PEPTIDE_CHAIN_ATOMNAME:
                        ca2 = atom
                        break

                if ca1 and ca2:
                    # Find the indices
                    idx1 = atoms.index(ca1)
                    idx2 = atoms.index(ca2)
                    bonds.append(
                        Bond(atom1_idx=idx1, atom2_idx=idx2, bond_type="single")
                    )

        # Add bonds within residues based on distance and element types
        for i, atom1 in enumerate(atoms):
            for j, atom2 in enumerate(atoms[i + 1 :], i + 1):
                # Check if atoms are in the same residue
                atom1_res = None
                atom2_res = None

                for res in residues:
                    if atom1 in res.atoms:
                        atom1_res = res
                    if atom2 in res.atoms:
                        atom2_res = res

                if atom1_res and atom2_res and atom1_res == atom2_res:
                    # Calculate distance
                    dist = np.sqrt(
                        (atom1.x - atom2.x) ** 2
                        + (atom1.y - atom2.y) ** 2
                        + (atom1.z - atom2.z) ** 2
                    )

                    # Simple bond detection based on distance and element types
                    if atoms_should_bond(atom1, atom2, dist):
                        bonds.append(Bond(atom1_idx=i, atom2_idx=j, bond_type=BondType.SINGLE))

        return bonds

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
