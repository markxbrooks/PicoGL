"""
Read PicoGL Data Script

This script demonstrates how to:
1. Read PicoGL data files (JSON format)
2. Understand the data structure
3. Convert the data back to PicoGL MeshData
4. Display the molecular structure
"""

import json
import os
import sys
from pathlib import Path

from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow


def load_picogl_data_file(file_path: str):
    """Load PicoGL data from a JSON file"""
    print(f"Loading PicoGL data from: {file_path}")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        print("✓ Successfully loaded PicoGL data file")
        return data

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def analyze_picogl_data(picogl_data):
    """Analyze and display information about the PicoGL data"""
    print(f"\n📊 PicoGL Data Analysis:")

    if "atoms" in picogl_data:
        atoms = picogl_data["atoms"]
        print(f"  Atoms:")
        print(f"    Count: {atoms.get('count', 'Unknown')}")
        print(f"    Positions: {len(atoms.get('positions', [])) // 3} vertices")
        print(f"    Colors: {len(atoms.get('colors', [])) // 3} colors")
        print(f"    Elements: {len(atoms.get('elements', []))} elements")

        # Show first few elements
        elements = atoms.get("elements", [])
        if elements:
            print(f"    Sample elements: {elements[:5]}")

    if "bonds" in picogl_data:
        bonds = picogl_data["bonds"]
        print(f"  Bonds:")
        print(f"    Count: {bonds.get('count', 'Unknown')}")
        print(f"    Positions: {len(bonds.get('positions', [])) // 3} vertices")
        print(f"    Colors: {len(bonds.get('colors', [])) // 3} colors")

    if "residues" in picogl_data:
        residues = picogl_data["residues"]
        print(f"  Residues: {len(residues)} total")
        if residues:
            print(f"    Sample residues: {residues[:5]}")

    if "chains" in picogl_data:
        chains = picogl_data["chains"]
        print(f"  Chains: {len(chains)} total")
        if chains:
            print(f"    Chain IDs: {chains}")


def create_mesh_from_picogl_data(picogl_data):
    """Create PicoGL MeshData from the loaded data"""
    print(f"\n🔧 Creating MeshData...")

    # Get atom data
    atom_positions = picogl_data.get("atoms", {}).get("positions", [])
    atom_colors = picogl_data.get("atoms", {}).get("colors", [])

    # Get bond data
    bond_positions = picogl_data.get("bonds", {}).get("positions", [])
    bond_colors = picogl_data.get("bonds", {}).get("colors", [])

    # Combine all vertices and colors
    all_vertices = atom_positions + bond_positions
    all_colors = atom_colors + bond_colors

    if not all_vertices:
        print("Error: No vertex data found")
        return None

    if not all_colors:
        print("Warning: No colour data found, using default colors")
        # Generate default colors (white)
        all_colors = [1.0, 1.0, 1.0] * (len(all_vertices) // 3)

    print(f"✓ Total vertices: {len(all_vertices) // 3}")
    print(f"✓ Total colors: {len(all_colors) // 3}")

    # Create MeshData
    mesh_data = MeshData.from_raw(vertices=all_vertices, colors=all_colors)

    print("✓ Successfully created MeshData")
    return mesh_data


def save_picogl_data_summary(picogl_data, output_file: str):
    """Save a summary of the PicoGL data"""
    print(f"\n💾 Saving data summary to: {output_file}")

    summary = {
        "summary": {
            "atoms_count": picogl_data.get("atoms", {}).get("count", 0),
            "bonds_count": picogl_data.get("bonds", {}).get("count", 0),
            "residues_count": len(picogl_data.get("residues", [])),
            "chains_count": len(picogl_data.get("chains", [])),
            "total_vertices": len(picogl_data.get("atoms", {}).get("positions", []))
            // 3
            + len(picogl_data.get("bonds", {}).get("positions", [])) // 3,
        },
        "metadata": {
            "file_type": "PicoGL Molecular Data",
            "version": "1.0",
            "description": "Molecular structure data converted from PDB format",
        },
    }

    try:
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        print("✓ Summary saved successfully")
    except Exception as e:
        print(f"Error saving summary: {e}")


def main():
    """Main function to demonstrate reading PicoGL data"""
    print("🔬 PicoGL Data Reader")
    print("=" * 50)

    # Check for input file argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Look for PicoGL data files in the current directory
        picogl_files = list(Path(".").glob("*_picogl.json"))

        if picogl_files:
            input_file = str(picogl_files[0])
            print(f"Found PicoGL data file: {input_file}")
        else:
            print("No PicoGL data file specified and none found in current directory.")
            print("\nUsage:")
            print(f"  python {sys.argv[0]} [path/to/picogl_data.json]")
            print("\nOr run the demo first to generate PicoGL data:")
            print("  python demo_pdb_molviewspec.py")
            return

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return

    try:
        # Load the PicoGL data
        picogl_data = load_picogl_data_file(input_file)
        if not picogl_data:
            return

        # Analyze the data
        analyze_picogl_data(picogl_data)

        # Create mesh data
        mesh_data = create_mesh_from_picogl_data(picogl_data)
        if not mesh_data:
            return

        # Save summary
        summary_file = "picogl_data_summary.json"
        save_picogl_data_summary(picogl_data, summary_file)

        # Create and run the render window
        print(f"\n🎮 Starting visualization...")
        render_window = RenderWindow(
            width=800,
            height=600,
            title=f"PicoGL Data Viewer - {os.path.basename(input_file)}",
            data=mesh_data,
            glsl_dir=Path(__file__).parent / "glsl" / "tu01",
            base_dir=Path(__file__).parent,
        )

        print("✓ Render window created")
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
