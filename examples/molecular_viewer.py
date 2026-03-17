"""
Molecular Viewer with PDB Support and MolViewSpec Integration

This example demonstrates how to:
1. Load PDB files using the PDBLoader
2. Visualize molecular structures with PicoGL
3. Export to MolViewSpec format for portable viewing
"""
import os
import sys
from pathlib import Path

import numpy as np
from OpenGL.GL import *
from utils.pdb_loader import PDBLoader

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.renderer import MeshData
from picogl.shaders.registry import ShaderRegistry
from picogl.shaders.type import ShaderType
from picogl.ui.backend.glut.window.object import RenderWindow

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class MolecularViewer:
    """Molecular structure viewer with PDB support"""

    def __init__(self, pdb_path: str):
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.atom_data = None
        self.bond_data = None

        # Load the PDB structure
        self._load_structure()

        # Initialize shaders
        self.shader_registry = ShaderRegistry()
        self._load_shaders()

    def _load_structure(self):
        """Load PDB structure and convert to PicoGL format"""
        print(f"Loading PDB structure from: {self.pdb_path}")
        self.pdb_loader = PDBLoader(self.pdb_path)

        # Convert to PicoGL data
        picogl_data = self.pdb_loader.to_picogl_data()

        self.atom_data = picogl_data["atoms"]
        self.bond_data = picogl_data["bonds"]

        print(
            f"Loaded {self.atom_data['count']} atoms and {self.bond_data['count']} bonds"
        )
        print(f"Residues: {len(picogl_data['residues'])}")
        print(f"Chains: {picogl_data['chains']}")

    def _load_shaders(self):
        """Load molecular visualization shaders"""
        print("Loading molecular visualization shaders...")

        # Load all available shader types
        for shader_type in ShaderType:
            try:
                self.shader_registry.load_and_add(shader_type)
                print(f"Loaded shader: {shader_type}")
            except Exception as e:
                print(f"Warning: Could not load shader {shader_type}: {e}")

    def create_atom_mesh(self) -> MeshData:
        """Create mesh data for atoms (spheres)"""
        if not self.atom_data:
            raise ValueError("No atom data loaded")

        # For now, we'll represent atoms as points
        # In a full implementation, you'd generate sphere geometry
        vertices = np.array(self.atom_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        colors = np.array(self.atom_data["colors"], dtype=np.float32).reshape(-1, 3)

        # Create indices for point rendering
        indices = np.arange(len(vertices), dtype=np.uint32)

        return MeshData.from_raw(
            vertices=vertices.flatten().tolist(),
            colors=colors.flatten().tolist(),
            indices=indices.tolist(),
        )

    def create_bond_mesh(self) -> MeshData:
        """Create mesh data for bonds (lines)"""
        if not self.bond_data:
            raise ValueError("No bond data loaded")

        # Bonds are already in line format (pairs of vertices)
        vertices = np.array(self.bond_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        colors = np.array(self.bond_data["colors"], dtype=np.float32).reshape(-1, 3)

        # Create indices for line rendering
        indices = np.arange(len(vertices), dtype=np.uint32)

        return MeshData.from_raw(
            vertices=vertices.flatten().tolist(),
            colors=colors.flatten().tolist(),
            indices=indices.tolist(),
        )

    def export_molviewspec(self, output_path: str):
        """Export the structure to MolViewSpec format"""
        if self.pdb_loader:
            molviewspec = self.pdb_loader.to_molviewspec()

            import json

            with open(output_path, "w") as f:
                json.dump(molviewspec, f, indent=2)

            print(f"Exported MolViewSpec to: {output_path}")
        else:
            print("No PDB structure loaded to export")


class MolecularRenderWindow(RenderWindow):
    """Specialized render window for molecular visualization"""

    def __init__(self, molecular_viewer: MolecularViewer, **kwargs):
        self.molecular_viewer = molecular_viewer
        self.atom_mesh = None
        self.bond_mesh = None

        # Create meshes
        self.atom_mesh = molecular_viewer.create_atom_mesh()
        self.bond_mesh = molecular_viewer.create_bond_mesh()

        super().__init__(**kwargs)

    def initialize(self):
        """Initialize the molecular viewer"""
        super().initialize()

        # Set up molecular-specific rendering
        self._setup_molecular_rendering()

    def _setup_molecular_rendering(self):
        """Set up molecular visualization specific rendering"""
        # Enable point sprites for atoms
        glEnable(GL_POINT_SPRITE)
        glEnable(GL_PROGRAM_POINT_SIZE)

        # Set point size for atoms
        glPointSize(8.0)

        # Enable line smoothing for bonds
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(2.0)

    def render(self):
        """Render the molecular structure"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Render bonds first (so they appear behind atoms)
        if self.bond_mesh:
            self._render_bonds()

        # Render atoms on top
        if self.atom_mesh:
            self._render_atoms()

    def _render_atoms(self):
        """Render atoms as points"""
        if not self.atom_mesh:
            return

        # Use the atoms shader if available
        atoms_shader = self.molecular_viewer.shader_registry.get(ShaderType.ATOMS)
        if atoms_shader:
            atoms_shader.bind()

            # Set uniforms
            atoms_shader.uniform("mvp_matrix", self.context.mvp_matrix)
            atoms_shader.uniform("point_size", 8.0)

            # Render atoms
            self._render_mesh(self.atom_mesh, GL_POINTS)

            atoms_shader.unbind()
        else:
            # Fallback to basic rendering
            self._render_mesh(self.atom_mesh, GL_POINTS)

    def _render_bonds(self):
        """Render bonds as lines"""
        if not self.bond_mesh:
            return

        # Use the bonds shader if available
        bonds_shader = self.molecular_viewer.shader_registry.get(ShaderType.BONDS)
        if bonds_shader:
            bonds_shader.bind()

            # Set uniforms
            bonds_shader.uniform("mvp_matrix", self.context.mvp_matrix)
            bonds_shader.uniform("line_width", 2.0)

            # Render bonds
            self._render_mesh(self.bond_mesh, GL_LINES)

            bonds_shader.unbind()
        else:
            # Fallback to basic rendering
            self._render_mesh(self.bond_mesh, GL_LINES)

    def _render_mesh(self, mesh: MeshData, mode: int):
        """Render a mesh with the given OpenGL mode"""
        # Create VAO for this mesh
        vao = VertexArrayObject()

        # Add vertex buffer
        vao.add_vbo(index=0, data=np.array(mesh.vertices, dtype=np.float32), size=3)

        # Add colour buffer if available
        if hasattr(mesh, "colors") and mesh.colors:
            vao.add_vbo(index=1, data=np.array(mesh.colors, dtype=np.float32), size=3)

        # Add index buffer if available
        if hasattr(mesh, "indices") and mesh.indices:
            vao.add_vbo(index=2, data=np.array(mesh.indices, dtype=np.uint32), size=1)
            vao.draw(mode=mode, index_count=len(mesh.indices))
        else:
            vao.draw(mode=mode, index_count=len(mesh.vertices) // 3)


def main():
    """Main function to demonstrate molecular viewing"""
    # Example PDB file path - you'll need to provide your own PDB file
    pdb_path = "data/2VUG.pdb"

    try:
        # Create molecular viewer
        viewer = MolecularViewer(pdb_path)

        # Export to MolViewSpec
        viewer.export_molviewspec("output.molviewspec")

        # Create render window
        render_window = MolecularRenderWindow(
            molecular_viewer=viewer,
            width=1024,
            height=768,
            title="Molecular Viewer - PDB Structure",
            data=viewer.create_atom_mesh(),  # Create atom mesh for base data
            glsl_dir=Path(__file__).parent / "glsl" / "tu01",
        )

        # Initialize and run
        render_window.initialize()
        render_window.run()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTo use this example:")
        print("1. Place a PDB file in the data/ directory")
        print("2. Update the pdb_path variable in main()")
        print("3. Run the script again")
        print("\nExample PDB files can be downloaded from:")
        print("- RCSB PDB: https://www.rcsb.org/")
        print("- AlphaFold DB: https://alphafold.ebi.ac.uk/")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
