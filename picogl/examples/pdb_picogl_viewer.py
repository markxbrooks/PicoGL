"""
PDB PicoGL Viewer

This script demonstrates how to:
1. Load PDB files using the PDBLoader
2. Convert them to PicoGL-compatible data
3. Render molecular structures with PicoGL
4. Display atoms and bonds in 3D space
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

from picogl.backend.gl.api.clear import gl_clear_color
from picogl.backend.gl.api.depth import gl_depth_func
from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums.point_size import (GLLegacyPointCapability,
                                                GLPointCapability)
from picogl.backend.gl.glfunc import GLDepthFunc
from picogl.examples.utils.pdb_loader import PDBLoader

# Add the current directory to the path to find pdb_loader.py
sys.path.insert(0, os.path.dirname(__file__))

try:
    # from pdb_loader import PDBLoader
    pass
except ImportError as e:
    print(f"Error importing PDB loader: {e}")
    print("Make sure pdb_loader.py is in the examples directory")
    sys.exit(1)

from OpenGL.GL import *

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow


def create_vao(mesh):
    vao = VertexArrayObject()
    atom_vertices = np.array(mesh.vertices, dtype=np.float32).reshape(-1, 3)
    atom_colors = np.array(mesh.colors, dtype=np.float32).reshape(-1, 3)

    vao.add_vbo(index=0, data=atom_vertices, size=3)
    vao.add_vbo(index=1, data=atom_colors, size=3)
    return vao


class MolecularRenderWindow(RenderWindow):
    """Specialized render window for molecular visualization with PicoGL"""

    def __init__(self, pdb_path: str, **kwargs):
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.atom_mesh = None
        self.bond_mesh = None
        self.atom_vao = None
        self.bond_vao = None

        # Load the PDB structure
        self._load_molecular_data()

        # Create meshes
        self._create_meshes()

        super().__init__(**kwargs)

    def _load_molecular_data(self):
        """Load PDB structure and convert to PicoGL data"""
        print(f"Loading PDB structure from: {self.pdb_path}")

        try:
            self.pdb_loader = PDBLoader(self.pdb_path)
            self.picogl_data = self.pdb_loader.to_picogl_data()

            print(f"✓ Loaded {self.picogl_data['atoms']['count']} atoms")
            print(f"✓ Loaded {self.picogl_data['bonds']['count']} bonds")
            print(f"✓ Structure: {self.pdb_loader.structure.title}")

        except Exception as e:
            print(f"Error loading PDB file: {e}")
            raise

    def _create_meshes(self):
        """Create PicoGL mesh data for atoms and bonds"""
        # Create atom mesh (points)
        atom_positions = np.array(
            self.picogl_data["atoms"]["positions"], dtype=np.float32
        )
        atom_colors = np.array(self.picogl_data["atoms"]["colors"], dtype=np.float32)

        self.atom_mesh = MeshData.from_raw(
            vertices=atom_positions.flatten().tolist(),
            colors=atom_colors.flatten().tolist(),
        )

        # Create bond mesh (lines)
        if self.picogl_data["bonds"]["count"] > 0:
            bond_positions = np.array(
                self.picogl_data["bonds"]["positions"], dtype=np.float32
            )
            bond_colors = np.array(
                self.picogl_data["bonds"]["colors"], dtype=np.float32
            )

            self.bond_mesh = MeshData.from_raw(
                vertices=bond_positions.flatten().tolist(),
                colors=bond_colors.flatten().tolist(),
            )

        print("✓ Created molecular meshes")

    def initialize(self):
        """Initialize the molecular viewer"""
        super().initialize()

        # Set up molecular-specific rendering
        self._setup_molecular_rendering()

        # Create VAOs for efficient rendering
        self._create_vaos()

    def _setup_molecular_rendering(self):
        """Set up molecular visualization specific rendering"""
        # Enable point sprites for atoms
        gl_enable(GLLegacyPointCapability.POINT_SPRITE)
        gl_enable(GLPointCapability.PROGRAM_POINT_SIZE)

        # Set point size for atoms
        glPointSize(8.0)

        # Enable line smoothing for bonds
        gl_enable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(2.0)

        # Enable depth testing
        gl_enable(GLPipelineCapability.DEPTH_TEST)
        gl_depth_func(GLDepthFunc.LESS)

        # Set background colour
        gl_clear_color((0.1, 0.1, 0.2, 1.0))

    def _create_vaos(self):
        """Create Vertex Array Objects for efficient rendering"""
        # Create VAO for atoms
        self.atom_vao = create_vao(self.atom_mesh)

        # Create VAO for bonds
        if self.bond_mesh:
            self.bond_vao = create_vao(self.bond_mesh)
        print("✓ Created VAOs for molecular rendering")

    def render(self):
        """Render the molecular structure"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Render bonds first (so they appear behind atoms)
        if self.bond_vao:
            self._render_bonds()

        # Render atoms on top
        if self.atom_vao:
            self._render_atoms()

    def _render_atoms(self):
        """Render atoms as points"""
        if not self.atom_vao:
            return

        # Use the shader program
        if hasattr(self, "context") and self.context.shader:
            shader = self.context.shader

            # Set uniforms
            if hasattr(self.context, "mvp_matrix"):
                shader.uniform("mvp_matrix", self.context.mvp_matrix)

            # Render atoms
            with self.atom_vao:
                glDrawArrays(GL_POINTS, 0, len(self.atom_mesh.vertices) // 3)
        else:
            # Fallback rendering without shader
            with self.atom_vao:
                glDrawArrays(GL_POINTS, 0, len(self.atom_mesh.vertices) // 3)

    def _render_bonds(self):
        """Render bonds as lines"""
        if not self.bond_vao:
            return

        # Use the shader program
        if hasattr(self, "context") and self.context.shader:
            shader = self.context.shader

            # Set uniforms
            if hasattr(self.context, "mvp_matrix"):
                shader.uniform("mvp_matrix", self.context.mvp_matrix)

            # Render bonds
            with self.bond_vao:
                glDrawArrays(GL_LINES, 0, len(self.bond_mesh.vertices) // 3)
        else:
            # Fallback rendering without shader
            with self.bond_vao:
                glDrawArrays(GL_LINES, 0, len(self.bond_mesh.vertices) // 3)

    def keyPressEvent(self, key, x, y):
        """Handle keyboard input"""
        if key == b"q" or key == b"Q":
            print("Quitting molecular viewer...")
            sys.exit(0)
        elif key == b"i" or key == b"I":
            self._print_structure_info()
        elif key == b"s" or key == b"S":
            self._save_molviewspec()
        elif key == b"h" or key == b"H":
            self._print_help()

    def _print_structure_info(self):
        """Print information about the loaded structure"""
        if self.pdb_loader and self.pdb_loader.structure:
            structure = self.pdb_loader.structure
            print(f"\n📊 Structure Information:")
            print(f"  Title: {structure.title}")
            print(f"  Atoms: {len(structure.atoms)}")
            print(f"  Bonds: {len(structure.bonds)}")
            print(f"  Residues: {len(structure.residues)}")
            print(f"  Chains: {structure.chains}")

    def _save_molviewspec(self):
        """Save the structure to MolViewSpec format"""
        if self.pdb_loader:
            try:
                molviewspec = self.pdb_loader.to_molviewspec()
                output_file = "molecular_structure.molviewspec"

                with open(output_file, "w") as f:
                    json.dump(molviewspec, f, indent=2)

                print(f"✓ Saved MolViewSpec to: {output_file}")
            except Exception as e:
                print(f"Error saving MolViewSpec: {e}")

    def _print_help(self):
        """Print help information"""
        print(f"\n🎮 Molecular Viewer Controls:")
        print(f"  Mouse: Rotate view")
        print(f"  Scroll: Zoom in/out")
        print(f"  I: Show structure information")
        print(f"  S: Save MolViewSpec file")
        print(f"  H: Show this help")
        print(f"  Q: Quit")


def main():
    """Main function to run the molecular viewer"""
    # Check for PDB file argument
    if len(sys.argv) > 1:
        pdb_path = sys.argv[1]
    else:
        # Default to example PDB file
        pdb_path = "data/example.pdb"

    # Check if PDB file exists
    if not os.path.exists(pdb_path):
        print(f"Error: PDB file not found: {pdb_path}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} [path/to/structure.pdb]")
        print("\nOr place a PDB file in the data/ directory and run:")
        print(f"  python {sys.argv[0]}")
        return

    try:
        # Create the molecular viewer window
        render_window = MolecularRenderWindow(
            pdb_path=pdb_path,
            width=1024,
            height=768,
            title=f"Molecular Viewer - {os.path.basename(pdb_path)}",
            data=None,  # We'll handle the data ourselves
            glsl_dir=Path(__file__).parent / "glsl" / "molecular",
            base_dir=Path(__file__).parent,
        )

        # Initialize and run
        render_window.initialize()
        render_window.run()

    except Exception as e:
        print(f"Error running molecular viewer: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
