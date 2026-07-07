# Qt Legacy Molecular Viewer

A simple Qt-based molecular viewer for PDB files that displays C-alpha atoms as a white wireframe model using legacy OpenGL.

## Features

- **PDB File Loading**: Loads and parses PDB files using the built-in PDBLoader
- **C-alpha Visualization**: Displays only C-alpha atoms (CA) as white wireframe spheres
- **Bond Display**: Shows bonds between consecutive C-alpha atoms in each chain
- **Interactive Controls**: Mouse rotation, zoom, and view reset
- **Legacy OpenGL**: Uses legacy OpenGL for maximum compatibility
- **PySide6 Interface**: Modern Qt interface with PySide6

## Files

- `qt_legacy_molecular_viewer.py` - Main molecular viewer application
- `test_molecular_viewer.py` - Test script to verify functionality
- `data/2VUG.pdb` - Sample PDB file (Archaeal RNA Ligase)

## Requirements

- Python 3.7+
- PySide6
- PyOpenGL
- NumPy
- PDBLoader (included in utils/)

## Installation

```bash
# Install PySide6
pip install PySide6

# Install other dependencies (if not already installed)
pip install PyOpenGL numpy
```

## Usage

### Run the Molecular Viewer

```bash
cd examples
python qt_legacy_molecular_viewer.py
```

### Test the Functionality

```bash
cd examples
python test_molecular_viewer.py
```

## Controls

- **Left Mouse Button + Drag**: Rotate the molecular structure
- **Mouse Wheel**: Zoom in/out
- **R Key**: Reset view to default
- **ESC Key**: Exit the application
- **Reset View Button**: Reset view to default
- **Show Info Button**: Display structure information

## Structure Information

The viewer displays:
- **Structure Title**: From the PDB file
- **C-alpha Atoms**: Count of C-alpha atoms found
- **C-alpha Bonds**: Count of bonds between consecutive C-alpha atoms
- **Chains**: Protein chains in the structure
- **Total Atoms**: All atoms in the PDB file

## Example Output

For the 2VUG.pdb file:
- **Structure**: THE STRUCTURE OF AN ARCHAEAL HOMODIMERIC RNA LIGASE
- **C-alpha Atoms**: 746 (373 per chain)
- **C-alpha Bonds**: 744 (372 per chain)
- **Chains**: A, B
- **Total Atoms**: 6,222

## Technical Details

### C-alpha Extraction

The viewer extracts C-alpha atoms by filtering for atoms with `name == "CA"`:

```python
calpha_atoms = [atom for atom in structure.atoms if atom.name.strip() == "CA"]
```

### Bond Generation

Bonds are created between consecutive C-alpha atoms in the same chain:

```python
# Only create bonds between consecutive residues
if atom2.res_seq == atom1.res_seq + 1:
    calpha_bonds.append((idx1, idx2))
```

### Rendering

- **Atoms**: White wireframe spheres using `gluSphere()` equivalent
- **Bonds**: White lines between connected C-alpha atoms
- **Background**: Black
- **Lighting**: Basic OpenGL lighting for depth perception

## Customization

### Change PDB File

Edit the `pdb_path` variable in `main()`:

```python
pdb_path = os.path.join(os.path.dirname(__file__), "data", "your_file.pdb")
```

### Modify Atom Size

Change the sphere radius in `_render_calpha_atoms()`:

```python
self._draw_wireframe_sphere(0.5, 8, 6)  # radius, slices, stacks
```

### Change Colors

Modify the color in `_render_calpha_atoms()` and `_render_calpha_bonds()`:

```python
glColor3f(1.0, 1.0, 1.0)  # White (R, G, B)
```

## Troubleshooting

### Import Errors

If you get import errors for PySide6:

```bash
pip install PySide6
```

### PDB File Not Found

Ensure the PDB file is in the `examples/data/` directory and the path is correct.

### OpenGL Issues

The viewer uses legacy OpenGL for maximum compatibility. If you encounter issues:

1. Update your graphics drivers
2. Ensure OpenGL is properly installed
3. Try running with different OpenGL contexts

### Performance Issues

For large structures:
- The viewer only displays C-alpha atoms (much fewer than total atoms)
- Wireframe rendering is efficient
- Consider reducing the sphere detail (slices, stacks) for better performance

## License

This molecular viewer is part of the PicoGL project and follows the same license terms.
