# Molecular Visualization with PDB Files and MolViewSpec

This guide explains how to use the PDB loader system to open PDB files and convert them to MolViewSpec format for portable molecular visualization.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install numpy
```

### 2. Basic Usage

```python
from utils.pdb_loader import PDBLoader

# Load a PDB file
loader = PDBLoader("path/to/structure.pdb")

# Convert to MolViewSpec
molviewspec = loader.to_molviewspec()

# Save for sharing
import json
with open("structure.molviewspec", "w") as f:
    json.dump(molviewspec, f, indent=2)
```

### 3. Run the Demo

```bash
cd examples
python demo_pdb_molviewspec.py
```

## 📁 File Structure

```
PicoGL/
├── examples/
│   ├── utils/
│   │   └── pdb_loader.py          # Core PDB loading functionality
│   ├── molecular_viewer.py        # Interactive molecular viewer
│   ├── demo_pdb_molviewspec.py    # Demonstration script
│   ├── data/
│   │   └── example.pdb            # Sample PDB file
│   └── README_MOLECULAR.md        # Detailed documentation
├── test_pdb_loader.py             # Test suite
└── MOLECULAR_VISUALIZATION_GUIDE.md  # This guide
```

## 🔬 What is MolViewSpec?

MolViewSpec is a portable format for molecular visualization scenes that can be opened in any compatible viewer. It's designed to be:

- **Portable**: Share molecular visualizations across different platforms
- **Standardized**: Compatible with multiple molecular viewers
- **Rich**: Supports atoms, bonds, surfaces, and other molecular representations
- **Extensible**: Easy to add new representation types

### Supported Viewers

- **Mol* Viewer**: https://molstar.org/ (Primary viewer)
- **NGL Viewer**: https://nglviewer.org/
- **PyMOL**: With appropriate plugins
- **VMD**: With appropriate plugins

## 📊 PDB File Support

The loader supports standard PDB format records:

- **ATOM/HETATM**: Atom coordinates and properties
- **CONECT**: Explicit bond connectivity  
- **TITLE**: Structure title and metadata
- **REMARK**: Comments and additional information

### Automatic Features

- **Bond Detection**: Automatically generates bonds if not provided
- **Residue Grouping**: Groups atoms by amino acid/residue
- **Chain Identification**: Detects protein chains
- **Element Recognition**: Identifies atom types from coordinates

## 💻 Code Examples

### Basic PDB Loading

```python
from utils.pdb_loader import PDBLoader

# Load structure
loader = PDBLoader("protein.pdb")
structure = loader.structure

# Access data
print(f"Atoms: {len(structure.atoms)}")
print(f"Bonds: {len(structure.bonds)}")
print(f"Residues: {len(structure.residues)}")
print(f"Chains: {structure.chains}")
```

### Structure Analysis

```python
# Analyze atom composition
elements = {}
for atom in structure.atoms:
    elements[atom.element] = elements.get(atom.element, 0) + 1

print("Element composition:")
for element, count in elements.items():
    print(f"  {element}: {count}")

# Find specific residues
ala_residues = [r for r in structure.residues if r.name == "ALA"]
print(f"Alanine residues: {len(ala_residues)}")
```

### MolViewSpec Export

```python
# Convert to MolViewSpec
molviewspec = loader.to_molviewspec()

# Customize the output
molviewspec["name"] = "My Protein Structure"
molviewspec["description"] = "Custom description"

# Save to file
import json
with open("custom_structure.molviewspec", "w") as f:
    json.dump(molviewspec, f, indent=2)
```

### PicoGL Integration

```python
# Convert to PicoGL data
picogl_data = loader.to_picogl_data()

# Access rendering data
atom_positions = picogl_data['atoms']['positions']
atom_colors = picogl_data['atoms']['colors']
bond_positions = picogl_data['bonds']['positions']

# Use with PicoGL renderers
from picogl.renderer import MeshData

mesh_data = MeshData.from_raw(
  vertices=atom_positions,
  colors=atom_colors
)
```

## 🎨 Visualization Options

### Representation Types

- **Ball-and-Stick**: Atoms as spheres, bonds as cylinders
- **Space-Filling**: Atoms as overlapping spheres
- **Ribbon**: Protein backbone as ribbons
- **Surface**: Molecular surface representation
- **Custom**: User-defined representations

### Color Schemes

- **Element-based**: Standard molecular colors (C=gray, N=blue, O=red, S=yellow)
- **Residue-based**: Color by amino acid type
- **Chain-based**: Different colors for different chains
- **Custom**: User-defined color schemes

## 🔧 Advanced Usage

### Custom Bond Detection

```python
# Override automatic bond detection
loader = PDBLoader("structure.pdb")

# Add custom bonds
from utils.pdb_loader import Bond
custom_bond = Bond(atom1_idx=0, atom2_idx=1, bond_type="custom")
loader.structure.bonds.append(custom_bond)
```

### Filtering Atoms

```python
# Load only specific atom types
atoms = [atom for atom in loader.structure.atoms if atom.element == "C"]

# Load only backbone atoms
backbone_atoms = [atom for atom in loader.structure.atoms 
                  if atom.name.strip() in ["N", "CA", "C", "O"]]
```

### Batch Processing

```python
import glob

# Process multiple PDB files
pdb_files = glob.glob("*.pdb")
for pdb_file in pdb_files:
    loader = PDBLoader(pdb_file)
    molviewspec = loader.to_molviewspec()
    
    output_file = f"{pdb_file.stem}.molviewspec"
    save_molviewspec(molviewspec, output_file)
```

## 📥 Getting PDB Files

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

### Download Methods

```bash
# Using wget
wget https://files.rcsb.org/download/1CRN.pdb

# Using curl
curl -O https://files.rcsb.org/download/1CRN.pdb

# Using Python
import requests
response = requests.get("https://files.rcsb.org/download/1CRN.pdb")
with open("1CRN.pdb", "w") as f:
    f.write(response.text)
```

## 🐛 Troubleshooting

### Common Issues

1. **File not found**: Check file path and permissions
2. **Parsing errors**: Verify PDB file format compliance
3. **Missing bonds**: Bonds are generated automatically
4. **Large files**: Very large structures may take time to process

### Performance Tips

- Use smaller PDB files for testing
- Filter atoms to reduce data size
- Use appropriate level of detail
- Consider using C-alpha only for large proteins

### Debug Mode

```python
# Enable verbose output
import logging
logging.basicConfig(level=logging.DEBUG)

# Load with error handling
try:
    loader = PDBLoader("structure.pdb")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

## 🔮 Future Enhancements

### Planned Features

- **MMCIF Support**: Extended molecular format
- **SDF Support**: Chemical structure format
- **Trajectory Support**: Molecular dynamics frames
- **Surface Generation**: Molecular surface calculation
- **Animation Support**: Time-series visualization

### Contributing

To extend the system:

1. **Add new file formats** in the loader
2. **Create custom representations** in MolViewSpec
3. **Implement new visualization styles** in PicoGL
4. **Add analysis tools** for molecular properties

## 📚 Additional Resources

### Documentation

- [MolViewSpec Specification](https://molviewspec.readthedocs.io/)
- [PicoGL Documentation](https://picogl.readthedocs.io/)
- [PDB Format Guide](https://www.wwpdb.org/documentation/file-format)

### Examples

- [Sample PDB Files](https://www.rcsb.org/structure/1CRN)
- [MolViewSpec Examples](https://github.com/molstar/molviewspec/tree/main/examples)
- [PicoGL Examples](examples/)

### Community

- [Mol* Discussion](https://github.com/molstar/molstar/discussions)
- [PicoGL Issues](https://github.com/markxbrooks/PicoGL/issues)

## 🎯 Summary

This system provides a complete pipeline for:

1. **Loading PDB files** with automatic parsing and validation
2. **Converting to MolViewSpec** for portable visualization
3. **Integrating with PicoGL** for custom rendering
4. **Sharing molecular structures** across platforms

The combination of PDB loading, MolViewSpec export, and PicoGL integration makes it easy to work with molecular structures in a portable, extensible way.

---

**Happy Molecular Visualization! 🧬✨**
