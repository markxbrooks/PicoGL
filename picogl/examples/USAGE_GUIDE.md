# PicoGL PDB Visualization Usage Guide

This guide explains how to use the various PicoGL scripts for loading PDB files and visualizing molecular structures.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Generate Sample Data

```bash
cd examples
python demo_pdb_molviewspec.py
```

This will create:
- `example.molviewspec` - MolViewSpec format
- `example_picogl.json` - PicoGL data format
- `example_summary.txt` - Structure summary

## 📁 Available Scripts

### 1. `demo_pdb_molviewspec.py` - Main Demo Script

**Purpose**: Demonstrates the complete PDB to MolViewSpec conversion pipeline.

**Usage**:
```bash
python demo_pdb_molviewspec.py [path/to/structure.pdb]
```

**Features**:
- Loads PDB files
- Converts to MolViewSpec format
- Exports PicoGL data
- Generates structure summaries

**Output Files**:
- `.molviewspec` - Portable molecular visualization
- `_picogl.json` - PicoGL rendering data
- `_summary.txt` - Structure information

### 2. `read_picogl_data_simple.py` - Data Reader

**Purpose**: Reads and analyzes PicoGL data files without requiring the full rendering system.

**Usage**:
```bash
python read_picogl_data_simple.py [path/to/picogl_data.json]
```

**Features**:
- Loads PicoGL JSON data files
- Analyzes molecular structure data
- Shows data statistics and structure
- Converts to simplified formats
- Generates data summaries

**Output Files**:
- `picogl_data_summary.json` - Data analysis summary
- `simple_molecular_data.json` - Simplified format

### 3. `pdb_picogl_simple.py` - Simple Viewer

**Purpose**: Loads PDB files and displays them using PicoGL rendering.

**Usage**:
```bash
python pdb_picogl_simple.py [path/to/structure.pdb]
```

**Features**:
- Loads PDB files directly
- Converts to PicoGL format
- Renders molecular structures
- Interactive 3D visualization

**Controls**:
- Mouse: Rotate view
- Scroll: Zoom in/out
- Q: Quit

### 4. `pdb_picogl_viewer.py` - Advanced Viewer

**Purpose**: Full-featured molecular viewer with advanced rendering capabilities.

**Usage**:
```bash
python pdb_picogl_viewer.py [path/to/structure.pdb]
```

**Features**:
- Advanced molecular rendering
- Separate atom and bond visualization
- Custom shader support
- Interactive controls
- MolViewSpec export

**Controls**:
- Mouse: Rotate view
- Scroll: Zoom in/out
- I: Show structure information
- S: Save MolViewSpec file
- H: Show help
- Q: Quit

## 🔄 Workflow Examples

### Basic Workflow

1. **Load PDB File**:
   ```bash
   python demo_pdb_molviewspec.py data/my_structure.pdb
   ```

2. **Analyze Data**:
   ```bash
   python read_picogl_data_simple.py my_structure_picogl.json
   ```

3. **View Structure**:
   ```bash
   python pdb_picogl_simple.py data/my_structure.pdb
   ```

### Advanced Workflow

1. **Generate All Formats**:
   ```bash
   python demo_pdb_molviewspec.py data/protein.pdb
   ```

2. **Custom Analysis**:
   ```bash
   python read_picogl_data_simple.py protein_picogl.json
   ```

3. **Advanced Visualization**:
   ```bash
   python pdb_picogl_viewer.py data/protein.pdb
   ```

## 📊 Data Formats

### PicoGL Data Structure

```json
{
  "atoms": {
    "positions": [x1, y1, z1, x2, y2, z2, ...],
    "colors": [r1, g1, b1, r2, g2, b2, ...],
    "elements": ["C", "N", "O", ...],
    "count": 9
  },
  "bonds": {
    "positions": [x1, y1, z1, x2, y2, z2, ...],
    "colors": [r1, g1, b1, r2, g2, b2, ...],
    "count": 9
  },
  "residues": ["ALA", "GLY"],
  "chains": [""]
}
```

### MolViewSpec Structure

```json
{
  "version": "1.0.0",
  "name": "Structure Title",
  "components": [
    {
      "type": "representation",
      "kind": "ball-and-stick",
      "data": { ... }
    }
  ]
}
```

## 🎯 Use Cases

### 1. **Data Analysis**
- Use `read_picogl_data_simple.py` to analyze molecular structures
- Generate statistics and summaries
- Convert between formats

### 2. **Visualization**
- Use `pdb_picogl_simple.py` for basic viewing
- Use `pdb_picogl_viewer.py` for advanced visualization
- Export to MolViewSpec for sharing

### 3. **Integration**
- Use PicoGL data in custom applications
- Convert to other formats
- Process multiple structures

### 4. **Sharing**
- Export MolViewSpec files for colleagues
- Use with Mol* Viewer or other compatible viewers
- Create portable molecular visualizations

## 🔧 Customization

### Modifying Rendering

Edit the viewer scripts to:
- Change colors and styles
- Add custom representations
- Modify interaction controls
- Implement new visualization modes

### Adding Formats

Extend the system to support:
- MMCIF files
- SDF files
- Custom molecular formats
- Trajectory data

### Custom Analysis

Modify the data reader to:
- Calculate molecular properties
- Analyze structure patterns
- Generate custom reports
- Export to other formats

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **File Not Found**: Check file paths and permissions
3. **Rendering Issues**: Verify OpenGL support and drivers
4. **Performance**: Use smaller structures for testing

### Debug Mode

Enable verbose output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Error Handling

All scripts include comprehensive error handling:
- File validation
- Data integrity checks
- Graceful fallbacks
- Helpful error messages

## 📚 Next Steps

### Learning Resources

- [MolViewSpec Documentation](https://molviewspec.readthedocs.io/)
- [PicoGL Examples](examples/)
- [Molecular Visualization Best Practices](MOLECULAR_VISUALIZATION_GUIDE.md)

### Advanced Features

- Custom shaders for molecular rendering
- Animation and trajectory support
- Surface generation and analysis
- Integration with other molecular tools

### Community

- Report issues on GitHub
- Contribute improvements
- Share custom visualizations
- Join molecular visualization discussions

---

**Happy Molecular Visualization! 🧬✨**
