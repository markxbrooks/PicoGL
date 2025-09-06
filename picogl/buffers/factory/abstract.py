"""
AbstractBufferFactory
"""
from collections import defaultdict
from typing import List, Optional

import numpy as np
from OpenGL.raw.GL._types import GL_FLOAT

from elmo.gl.buffers.factory.helpers import prepare_atom_buffer_data, prepare_bond_buffer_data
from elmo.gl.buffers.molecule.calpha import CalphaVAOChainGroup
from elmo.gl.buffers.molecule.ribbon import RibbonVAOChainGroup
from elmo.logger import Logger as log
from elmo.pdb.structure.ribbon import generate_ribbon_geometry_per_chain_color_by_ca
from picogl.buffers.attributes import LayoutDescriptor, AttributeSpec
from picogl.error import gl_check_error
from picogl.renderer import MeshData


class AbstractBufferFactory:
    """Abstract Buffer Factory for molecular VAO/VBO creation."""

    # ---------------- Atom Buffers ---------------- #
    def create_atom_buffers(
        self, atoms: List["Atom3D"]
    ) -> Optional["VertexBufferGroup"]:
        """
        Create VAO and VBO for atom positions and colors.

        :param atoms: List of Atom3D
        :return: VertexBufferGroup or None
        """
        if not atoms:
            return None
        try:
            positions, colors = prepare_atom_buffer_data(atoms)

            normals = np.array(
                [
                    pos / np.linalg.norm(pos) if np.linalg.norm(pos) > 0 else [0, 0, 1]
                    for pos in positions
                ],
                dtype=np.float32,
            )
            return self.setup_atom_buffers(colors, normals, positions)
        except Exception as ex:
            log.error(f"Error creating atom buffers: {ex}")
            return None

    # ---------------- Bond Buffers ---------------- #
    def create_bond_buffers(
        self, atoms: List["Atom3D"], color_bonds: bool = True
    ) -> Optional["VertexBufferGroup"]:
        """
        Create bond buffers with optional per-atom colors.

        :param atoms: List of Atom3D
        :param color_bonds: Whether to color bonds per atom
        :return: VertexBufferGroup or None
        """
        if not atoms:
            return None

        try:
            bond_indices, colors, normals, positions = prepare_bond_buffer_data(
                atoms=atoms, color_bonds=color_bonds
            )
            bond_indices_flat = bond_indices.ravel()
            return self.setup_bond_buffers(
                bond_indices_flat, colors, normals, positions
            )
        except Exception as ex:
            log.error(f"Error creating bond buffers: {ex}")
            return None

    # ---------------- Calpha Buffers ---------------- #
    def create_calpha_buffers(
        self, atoms: List["Atom3D"], chain_colors: dict
    ) -> Optional["CalphaVAOChainGroup"]:
        """
        Create Calpha buffers grouped by chain.

        :param atoms: List of Atom3D
        :param chain_colors: dict mapping chain_id to color
        :return: CalphaVAOChainGroup or None
        """
        if not atoms:
            return None

        calpha_group = CalphaVAOChainGroup()
        atoms_by_chain = defaultdict(list)
        for atom in atoms:
            atoms_by_chain[atom.chain_id].append(atom)

        for chain_id, chain_atoms in atoms_by_chain.items():
            if len(chain_atoms) < 2:
                continue

            positions = np.array(
                [atom.coords for atom in chain_atoms], dtype=np.float32
            )
            color = chain_colors.get(chain_id, (1.0, 0.0, 0.0))
            colors = np.tile(color, (len(chain_atoms), 1)).astype(np.float32)

            vao = self.setup_calpha_buffers(colors, positions)
            if vao:
                calpha_group.per_chain[chain_id] = vao
                calpha_group.num_vertices_per_chain[chain_id] = len(chain_atoms)

        return calpha_group if calpha_group.per_chain else None

    # ---------------- Ribbon Buffers ---------------- #
    def create_ribbon_buffers(
        self,
        all_ca_coords: np.ndarray,
        all_chain_ids: List[str],
        all_ca_colors: np.ndarray,
        show_arrow: bool = False,
    ) -> Optional["RibbonVAOChainGroup"]:
        """
        Create VAO/VBO for ribbons for each chain.

        :param all_ca_coords: np.ndarray of shape (N, 3)
        :param all_chain_ids: List of chain IDs corresponding to coordinates
        :param all_ca_colors: np.ndarray of shape (N, 3) per CA
        :param show_arrow: Whether to add an arrow at the end
        :return: RibbonVAOChainGroup or None
        """
        if all_ca_coords.size == 0:
            return None

        ribbon_group = RibbonVAOChainGroup()
        try:
            ribbon_per_chain = generate_ribbon_geometry_per_chain_color_by_ca(
                all_ca_coords, all_chain_ids, all_ca_colors
            )

            for chain_id, data in ribbon_per_chain.items():
                ribbon_vao = self.setup_ribbon_vbg(data=data)
                ribbon_group.per_chain[chain_id] = ribbon_vao
                gl_check_error(f"GL Error in Ribbon chain ID {chain_id}")

            return ribbon_group if ribbon_group.per_chain else None
        except Exception as ex:
            log.error(f"❌ Ribbon buffer upload failed: {ex}")
            return None

    # ---------------- Abstract Setup Methods ---------------- #
    def setup_atom_buffers(self, colors, normals, positions):
        """Setup VAO and VBO for atoms. Implement in subclass."""
        raise NotImplementedError

    def setup_bond_buffers(self, bond_indices_flat, colors, normals, positions):
        """Setup VAO and VBO for bonds. Implement in subclass."""
        raise NotImplementedError

    def setup_calpha_buffers(self, colors, positions):
        """Setup VAO and VBO for Calpha. Implement in subclass."""
        raise NotImplementedError

    def setup_ribbon_vbg(self, data: MeshData):
        """Setup VAO and VBO for ribbons. Implement in subclass."""
        raise NotImplementedError

    # ---------------- Layout Helpers ---------------- #
    def create_layout(self, attributes):
        return LayoutDescriptor(attributes=attributes)

    def common_attributes(self):
        return [
            AttributeSpec(
                name="positions",
                index=0,
                size=3,
                type=GL_FLOAT,
                normalized=False,
                stride=0,
                offset=0,
            ),
            AttributeSpec(
                name="colors",
                index=1,
                size=3,
                type=GL_FLOAT,
                normalized=False,
                stride=0,
                offset=0,
            ),
        ]

    def setup_atom_layout(self):
        return self.create_layout(
            self.common_attributes()
            + [
                AttributeSpec(
                    name="normals",
                    index=2,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                )
            ]
        )

    def setup_bond_layout(self):
        return self.create_layout(
            self.common_attributes()
            + [
                AttributeSpec(
                    name="normals",
                    index=2,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                ),
                AttributeSpec(
                    name="ebo",
                    index=3,
                    size=2,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                ),
            ]
        )

    def setup_calpha_layout(self):
        return self.create_layout(self.common_attributes())
