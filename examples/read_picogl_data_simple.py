#!/usr/bin/env python3
"""
Simple PicoGL Data Reader

This script demonstrates how to read and analyze PicoGL data files
without requiring the full rendering system.
"""

import json
import os
import sys
from pathlib import Path


def load_picogl_data_file(file_path: str):
    """Load PicoGL data from a JSON file"""
    print(f"Loading PicoGL data from: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
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
    
    if 'atoms' in picogl_data:
        atoms = picogl_data['atoms']
        print(f"  Atoms:")
        print(f"    Count: {atoms.get('count', 'Unknown')}")
        print(f"    Positions: {len(atoms.get('positions', [])) // 3} vertices")
        print(f"    Colors: {len(atoms.get('colors', [])) // 3} colors")
        print(f"    Elements: {len(atoms.get('elements', []))} elements")
        
        # Show first few elements
        elements = atoms.get('elements', [])
        if elements:
            print(f"    Sample elements: {elements[:5]}")
    
    if 'bonds' in picogl_data:
        bonds = picogl_data['bonds']
        print(f"  Bonds:")
        print(f"    Count: {bonds.get('count', 'Unknown')}")
        print(f"    Positions: {len(bonds.get('positions', [])) // 3} vertices")
        print(f"    Colors: {len(bonds.get('colors', [])) // 3} colors")
    
    if 'residues' in picogl_data:
        residues = picogl_data['residues']
        print(f"  Residues: {len(residues)} total")
        if residues:
            print(f"    Sample residues: {residues[:5]}")
    
    if 'chains' in picogl_data:
        chains = picogl_data['chains']
        print(f"  Chains: {len(chains)} total")
        if chains:
            print(f"    Chain IDs: {chains}")


def show_data_structure(picogl_data):
    """Show the structure of the PicoGL data"""
    print(f"\n🏗️  Data Structure:")
    
    def print_structure(data, indent=0):
        for key, value in data.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}: {{")
                print_structure(value, indent + 1)
                print("  " * indent + "}")
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], (int, float)):
                    print("  " * indent + f"{key}: [{len(value)} values]")
                else:
                    print("  " * indent + f"{key}: [{len(value)} items]")
            else:
                print("  " * indent + f"{key}: {value}")
    
    print_structure(picogl_data)


def save_data_summary(picogl_data, output_file: str):
    """Save a summary of the PicoGL data"""
    print(f"\n💾 Saving data summary to: {output_file}")
    
    summary = {
        "summary": {
            "atoms_count": picogl_data.get('atoms', {}).get('count', 0),
            "bonds_count": picogl_data.get('bonds', {}).get('count', 0),
            "residues_count": len(picogl_data.get('residues', [])),
            "chains_count": len(picogl_data.get('chains', [])),
            "total_vertices": len(picogl_data.get('atoms', {}).get('positions', [])) // 3 + 
                             len(picogl_data.get('bonds', {}).get('positions', [])) // 3
        },
        "metadata": {
            "file_type": "PicoGL Molecular Data",
            "version": "1.0",
            "description": "Molecular structure data converted from PDB format"
        }
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print("✓ Summary saved successfully")
    except Exception as e:
        print(f"Error saving summary: {e}")


def convert_to_simple_format(picogl_data):
    """Convert PicoGL data to a simpler format for other applications"""
    print(f"\n🔄 Converting to simple format...")
    
    simple_data = {
        "vertices": [],
        "colors": [],
        "elements": [],
        "metadata": {
            "source": "PicoGL Data",
            "atoms_count": picogl_data.get('atoms', {}).get('count', 0),
            "bonds_count": picogl_data.get('bonds', {}).get('count', 0)
        }
    }
    
    # Add atom data
    atom_positions = picogl_data.get('atoms', {}).get('positions', [])
    atom_colors = picogl_data.get('atoms', {}).get('colors', [])
    atom_elements = picogl_data.get('atoms', {}).get('elements', [])
    
    for i in range(0, len(atom_positions), 3):
        simple_data["vertices"].append(atom_positions[i:i+3])
        simple_data["colors"].append(atom_colors[i:i+3])
        if atom_elements:
            simple_data["elements"].append(atom_elements[i//3])
    
    # Add bond data
    bond_positions = picogl_data.get('bonds', {}).get('positions', [])
    bond_colors = picogl_data.get('bonds', {}).get('colors', [])
    
    for i in range(0, len(bond_positions), 3):
        simple_data["vertices"].append(bond_positions[i:i+3])
        simple_data["colors"].append(bond_colors[i:i+3])
        simple_data["elements"].append("BOND")
    
    print(f"✓ Converted to simple format with {len(simple_data['vertices'])} vertices")
    return simple_data


def main():
    """Main function to demonstrate reading PicoGL data"""
    print("🔬 PicoGL Data Reader (Simple)")
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
        
        # Show data structure
        show_data_structure(picogl_data)
        
        # Save summary
        summary_file = "picogl_data_summary.json"
        save_data_summary(picogl_data, summary_file)
        
        # Convert to simple format
        simple_data = convert_to_simple_format(picogl_data)
        simple_file = "simple_molecular_data.json"
        with open(simple_file, 'w') as f:
            json.dump(simple_data, f, indent=2)
        print(f"✓ Saved simple format to: {simple_file}")
        
        print(f"\n🎉 Data analysis completed!")
        print(f"Files created:")
        print(f"  - {summary_file}: Data summary")
        print(f"  - {simple_file}: Simple format data")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
