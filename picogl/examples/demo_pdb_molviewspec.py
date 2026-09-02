#!/usr/bin/env python3
"""
PDB to MolViewSpec Conversion Demo

This script demonstrates how to:
1. Load PDB files
2. Convert them to MolViewSpec format
3. Save the results for portable viewing
"""

import json
import os
import sys
from pathlib import Path

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

try:
    from picogl.examples.pdb_loader import PDBLoader, save_molviewspec
except ImportError as e:
    print(f"Error importing PDB loader: {e}")
    print("Make sure you're running this from the examples directory")
    sys.exit(1)


def download_sample_pdb():
    """Download a sample PDB file for demonstration"""
    import urllib.request

    # Download a small protein structure (Crambin - 46 residues)
    pdb_id = "1CRN"
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    output_file = f"data/{pdb_id}.pdb"

    print(f"Downloading {pdb_id} from RCSB PDB...")

    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Download the file
        urllib.request.urlretrieve(url, output_file)
        print(f"✓ Downloaded {pdb_id}.pdb successfully")
        return output_file

    except Exception as e:
        print(f"✗ Failed to download {pdb_id}.pdb: {e}")
        return None


def analyze_structure(loader):
    """Analyze the loaded structure and print statistics"""
    structure = loader.structure

    print(f"\n📊 Structure Analysis:")
    print(f"  Title: {structure.title}")
    print(f"  Total Atoms: {len(structure.atoms)}")
    print(f"  Total Bonds: {len(structure.bonds)}")
    print(f"  Total Residues: {len(structure.residues)}")
    print(f"  Chains: {', '.join(structure.chains) if structure.chains else 'None'}")

    # Analyze atom types
    elements = {}
    for atom in structure.atoms:
        elements[atom.element] = elements.get(atom.element, 0) + 1

    print(f"  Element Composition:")
    for element, count in sorted(elements.items()):
        print(f"    {element}: {count}")

    # Analyze residue types
    residues = {}
    for residue in structure.residues:
        residues[residue.name] = residues.get(residue.name, 0) + 1

    print(f"  Residue Types:")
    for residue, count in sorted(residues.items()):
        print(f"    {residue}: {count}")


def export_formats(loader, base_name):
    """Export the structure in multiple formats"""
    print(f"\n💾 Exporting Structure...")

    # Export to MolViewSpec
    molviewspec_file = f"{base_name}.molviewspec"
    molviewspec = loader.to_molviewspec()
    save_molviewspec(molviewspec, molviewspec_file)
    print(f"  ✓ MolViewSpec: {molviewspec_file}")

    # Export to PicoGL data
    picogl_data = loader.to_picogl_data()
    picogl_file = f"{base_name}_picogl.json"
    with open(picogl_file, "w") as f:
        json.dump(picogl_data, f, indent=2)
    print(f"  ✓ PicoGL Data: {picogl_file}")

    # Export summary
    summary_file = f"{base_name}_summary.txt"
    with open(summary_file, "w") as f:
        f.write(f"Structure Summary: {loader.structure.title}\n")
        f.write(f"Atoms: {len(loader.structure.atoms)}\n")
        f.write(f"Bonds: {len(loader.structure.bonds)}\n")
        f.write(f"Residues: {len(loader.structure.residues)}\n")
        f.write(f"Chains: {', '.join(loader.structure.chains)}\n")
    print(f"  ✓ Summary: {summary_file}")


def show_molviewspec_info(molviewspec):
    """Display information about the generated MolViewSpec"""
    print(f"\nMolViewSpec Information:")
    print(f"  Version: {molviewspec.get('version', 'Unknown')}")
    print(f"  Name: {molviewspec.get('name', 'Unknown')}")
    print(f"  Description: {molviewspec.get('description', 'None')}")
    print(f"  Components: {len(molviewspec.get('components', []))}")

    for i, component in enumerate(molviewspec.get("components", [])):
        comp_type = component.get("type", "Unknown")
        comp_kind = component.get("kind", "Unknown")
        print(f"    Component {i+1}: {comp_type} - {comp_kind}")


def main():
    """Main demonstration function"""
    print("🧬 PDB to MolViewSpec Conversion Demo")
    print("=" * 50)

    # Check if we have a PDB file
    pdb_files = []

    # Look for PDB files in the data directory
    data_dir = Path("data")
    if data_dir.exists():
        pdb_files = list(data_dir.glob("*.pdb"))

    if not pdb_files:
        print("No PDB files found in data/ directory.")
        print("Downloading a sample PDB file...")

        sample_file = download_sample_pdb()
        if sample_file:
            pdb_files = [Path(sample_file)]
        else:
            print("Could not download sample PDB file.")
            print("Please place a PDB file in the data/ directory and run again.")
            return

    # Process each PDB file
    for pdb_file in pdb_files:
        print(f"\n📁 Processing: {pdb_file.name}")
        print("-" * 30)

        try:
            # Load the PDB file
            loader = PDBLoader(str(pdb_file))

            # Analyze the structure
            analyze_structure(loader)

            # Export in various formats
            base_name = pdb_file.stem
            export_formats(loader, base_name)

            # Show MolViewSpec information
            molviewspec = loader.to_molviewspec()
            show_molviewspec_info(molviewspec)

            print(f"\n✅ Successfully processed {pdb_file.name}")

        except Exception as e:
            print(f"❌ Error processing {pdb_file.name}: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n🎉 Demo completed!")
    print(f"\nNext steps:")
    print(f"1. Open the .molviewspec files in Mol* Viewer (https://molstar.org/)")
    print(f"2. Use the PicoGL data for custom visualization")
    print(f"3. Share the MolViewSpec files with colleagues")


if __name__ == "__main__":
    main()
