"""
Simple PDB PicoGL Viewer

This script demonstrates how to:
1. Load PDB files and convert to PicoGL data
2. Display the molecular structure using PicoGL
3. Simple rendering without complex shaders
"""

import os
import sys
from pathlib import Path

from picogl.examples.utils.pdb_loader import PDBLoader

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow


def load_pdb_as_picogl_data(pdb_path: str):
    """Load a PDB file and convert it to PicoGL-compatible data"""
    print(f"Loading PDB file: {pdb_path}")

    # Load the PDB structure
    loader = PDBLoader(pdb_path)

    # Convert to PicoGL data
    picogl_data = loader.to_picogl_data()

    print(f"✓ Loaded {picogl_data['atoms']['count']} atoms")
    print(f"✓ Loaded {picogl_data['bonds']['count']} bonds")
    print(f"✓ Structure: {loader.structure.title}")

    return picogl_data


def create_molecular_mesh_data(picogl_data):
    """Create MeshData from PicoGL molecular data"""
    # For simplicity, we'll combine atoms and bonds into one mesh
    # Atoms will be rendered as points, bonds as lines

    # Get atom data
    atom_positions = picogl_data["atoms"]["positions"]
    atom_colors = picogl_data["atoms"]["colors"]

    # Get bond data
    bond_positions = picogl_data["bonds"]["positions"]
    bond_colors = picogl_data["bonds"]["colors"]

    # Combine vertices and colors
    all_vertices = atom_positions + bond_positions
    all_colors = atom_colors + bond_colors

    print(f"✓ Created mesh with {len(all_vertices) // 3} total vertices")

    return MeshData.from_raw(vertices=all_vertices, colors=all_colors)


def main():
    """Main function to demonstrate PDB to PicoGL visualization"""
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
        # Load PDB and convert to PicoGL data
        picogl_data = load_pdb_as_picogl_data(pdb_path)

        # Create mesh data for rendering
        mesh_data = create_molecular_mesh_data(picogl_data)

        # Create and run the render window
        render_window = RenderWindow(
            width=800,
            height=600,
            title=f"Molecular Structure - {os.path.basename(pdb_path)}",
            data=mesh_data,
            glsl_dir=Path(__file__).parent / "glsl" / "tu01",  # Use existing shaders
            base_dir=Path(__file__).parent,
        )

        print("✓ Created render window")
        print("🎮 Controls:")
        print("  Mouse: Rotate view")
        print("  Scroll: Zoom in/out")
        print("  Q: Quit")

        # Initialize and run
        render_window.initialize()
        render_window.run()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
