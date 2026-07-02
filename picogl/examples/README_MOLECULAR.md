# Molecular Visualization with PDB Files and MolViewSpec

This directory contains tools for loading PDB (Protein Data Bank) files and visualizing molecular structures using PicoGL, with the ability to export to MolViewSpec format for portable viewing.

## Features

- **PDB File Loading**: Parse standard PDB format files
- **Molecular Visualization**: Render atoms and bonds using PicoGL
- **MolViewSpec Export**: Generate portable molecular visualization scenes
- **Automatic Bond Detection**: Intelligently determine molecular connectivity
- **Element-based Coloring**: Standard molecular visualization colors
- **Multiple Representation Styles**: Support for different rendering modes

## Files

- `pdb_loader.py` - Core PDB parsing and conversion functionality
- `molecular_viewer.py` - Interactive molecular visualization application
- `data/example.pdb` - Sample PDB file for testing

## Quick Start

### 1. Basic PDB Loading

```python
from utils.pdb_loader import PDBLoader

# Load a PDB file
loader = PDBLoader("path/to/your/structure.pdb")

# Access the structure data
structure = loader.structure
print(f"Loaded {len(structure.atoms)} atoms")
print(f"Found {len(structure.bonds)} bonds")
print(f"Structure has {len(structure.chains)} chains")
```

### 2. Export to MolViewSpec

```python
# Convert to MolViewSpec format
molviewspec = loader.to_molviewspec()

# Save to file
import json
with open("structure.molviewspec", "w") as f:
    json.dump(molviewspec, f, indent=2)
```

### 3. Use with PicoGL

```python
# Convert to PicoGL-compatible data
picogl_data = loader.to_picogl_data()

# Access atom and bond data
atom_positions = picogl_data['atoms']['positions']
atom_colors = picogl_data['atoms']['colors']
bond_positions = picogl_data['bonds']['positions']
```

### 4. Run the Molecular Viewer

```bash
cd examples
python3 molecular_viewer.py
```

## PDB File Format Support

The loader supports standard PDB format records:

- **ATOM/HETATM**: Atom coordinates and properties
- **CONECT**: Explicit bond connectivity
- **TITLE**: Structure title
- **REMARK**: Comments and metadata

### Automatic Bond Detection

If no explicit bonds are provided in the PDB file, the loader will automatically generate bonds based on:

1. **Peptide bonds** between consecutive residues
2. **Distance-based detection** using standard covalent bond lengths
3. **Element type compatibility** (C-C, C-N, C-O, etc.)

## MolViewSpec Integration

MolViewSpec is a portable format for molecular visualization scenes that can be opened in any compatible viewer.

### Generated MolViewSpec Structure

```json
{
  "version": "1.0.0",
  "name": "Structure Title",
  "description": "PDB structure description",
  "camera": {
    "position": [0, 0, 50],
    "target": [0, 0, 0],
    "up": [0, 1, 0]
  },
  "components": [
    {
      "type": "representation",
      "kind": "ball-and-stick",
      "props": {
        "alpha": 1.0,
        "color": "element-symbol"
      },
      "data": {
        "x": [...],
        "y": [...],
        "z": [...],
        "element": [...],
        "residue_name": [...],
        "residue_seq": [...],
        "chain_id": [...]
      }
    }
  ]
}
```

### Opening MolViewSpec Files

MolViewSpec files can be opened in various molecular viewers:

- **Mol* Viewer**: https://molstar.org/
- **NGL Viewer**: https://nglviewer.org/
- **PyMOL**: With appropriate plugins
- **VMD**: With appropriate plugins

## PicoGL Integration

The molecular visualization system integrates with PicoGL's existing shader infrastructure:

### Available Shader Types

- `atoms` - Atom rendering (spheres/points)
- `bonds` - Bond rendering (lines/cylinders)
- `calphas` - C-alpha backbone visualization
- `ribbons` - Protein ribbon diagrams

### Custom Shaders

You can create custom molecular visualization shaders by following the naming convention:

- `atoms_vert.glsl` - Vertex shader for atoms
- `atoms_frag.glsl` - Fragment shader for atoms
- `bonds_vert.glsl` - Vertex shader for bonds
- `bonds_frag.glsl` - Fragment shader for bonds

## Example Usage Scenarios

### 1. Protein Structure Analysis

```python
# Load a protein structure
loader = PDBLoader("protein.pdb")

# Analyze structure properties
atoms = loader.structure.atoms
residues = loader.structure.residues

# Find specific residues
ala_residues = [r for r in residues if r.name == "ALA"]
print(f"Found {len(ala_residues)} alanine residues")

# Export for sharing
loader.to_molviewspec("protein_analysis.molviewspec")
```

### 2. Molecular Dynamics Visualization

```python
# Load trajectory frames
frames = []
for i in range(100):
    frame_loader = PDBLoader(f"frame_{i:04d}.pdb")
    frames.append(frame_loader.structure)

# Create animation MolViewSpec
# (Implementation depends on specific needs)
```

### 3. Structure Comparison

```python
# Load multiple structures
struct1 = PDBLoader("structure1.pdb").structure
struct2 = PDBLoader("structure2.pdb").structure

# Compare properties
print(f"Structure 1: {len(struct1.atoms)} atoms")
print(f"Structure 2: {len(struct2.atoms)} atoms")
```

## Getting PDB Files

### Public Databases

- **RCSB PDB**: https://www.rcsb.org/
  - Search and download structures
  - API access available
  
- **AlphaFold DB**: https://alphafold.ebi.ac.uk/
  - Predicted protein structures
  - High-quality models for most proteins

- **PDB-101**: https://pdb101.rcsb.org/
  - Educational resources
  - Curated structure collections

### Downloading Structures

```bash
# Using wget
wget https://files.rcsb.org/download/1CRN.pdb

# Using curl
curl -O https://files.rcsb.org/download/1CRN.pdb

# Using Python requests
import requests
response = requests.get("https://files.rcsb.org/download/1CRN.pdb")
with open("1CRN.pdb", "w") as f:
    f.write(response.text)
```

## Troubleshooting

### Common Issues

1. **File not found**: Ensure the PDB file path is correct
2. **Parsing errors**: Check that the PDB file follows standard format
3. **Missing bonds**: The loader will generate bonds automatically
4. **Large files**: Very large structures may take time to process

### Performance Tips

- Use smaller PDB files for testing
- Consider filtering atoms (e.g., only C-alpha atoms for proteins)
- Use appropriate level of detail for your visualization needs

## Contributing

To extend the molecular visualization system:

1. **Add new representation types** in the PDB loader
2. **Create custom shaders** for specific visualization needs
3. **Implement additional file formats** (MMCIF, SDF, etc.)
4. **Add analysis tools** for molecular properties

## Dependencies

- `numpy` - Numerical operations
- `picogl` - OpenGL rendering framework
- `OpenGL` - Graphics API bindings

## License

This code is part of the PicoGL project. See the main project license for details.
