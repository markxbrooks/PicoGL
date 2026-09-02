# Legacy Cube Examples for PicoGL

This directory contains several cube rendering examples designed to work on systems with limited OpenGL support, including older macOS systems.

## Examples Overview

### 1. `cube.py` (Original - May not work on all systems)
- Uses modern `RenderWindow` with OpenGL 3.3+ shaders
- Requires shader files and modern OpenGL support
- May fail on older macOS systems or systems without shader support

### 2. `legacy_cube_fixed.py` (Recommended for PicoGL integration)
- Uses `LegacyGLMesh` for OpenGL 1.x/2.x compatibility
- Loads cube data using PicoGL MeshData
- Falls back to wireframe cube if mesh loading fails
- Works on systems without modern shader support

### 3. `legacy_cube_minimal.py` (Recommended for maximum compatibility)
- Uses only built-in OpenGL primitives (immediate mode)
- No external dependencies beyond PyOpenGL
- Maximum compatibility with older systems
- Works on any system with basic OpenGL support

## System Requirements

### Minimum Requirements
- Python 3.7+
- PyOpenGL
- GLUT (usually included with PyOpenGL)
- Basic OpenGL 1.x support

### Recommended for `legacy_cube_fixed.py`
- Python 3.7+
- PyOpenGL
- GLUT
- NumPy
- PicoGL library

## Installation

```bash
# Install required packages
pip install PyOpenGL PyOpenGL_accelerate numpy

# If using the fixed version with PicoGL support
pip install picogl  # Install PicoGL library
```

## Usage

### Minimal Cube (Maximum Compatibility)
```bash
cd examples
python legacy_cube_minimal.py
```

### Fixed Cube with PicoGL Support
```bash
cd examples
python legacy_cube_fixed.py
```

### Original Cube (Modern OpenGL)
```bash
cd examples
python legacy_cube_with_controls.py
```

## Controls

All examples support the following controls:

- **Mouse**: Rotate view
- **Mouse Wheel**: Zoom in/out
- **R**: Reset rotation
- **W**: Toggle wireframe mode
- **F**: Fill mode
- **+/-**: Zoom in/out
- **ESC**: Exit

Additional controls for `legacy_cube_minimal.py`:
- **N**: Toggle normals display
- **Space**: Toggle auto-rotation

## Features

### Cube Data
The cube examples use the same vertex and color data as the original `cube.py`:
- **36 vertices** (12 triangles × 3 vertices each)
- **36 colors** (one per vertex)
- **Colorful cube** with the same appearance as the original

### Rendering Modes
- **Fill mode**: Solid colored cube with lighting
- **Wireframe mode**: Red wireframe cube
- **Normals display**: Green normal vectors (minimal version only)

### Animation
- **Auto-rotation**: Press Space to toggle continuous rotation
- **Manual rotation**: Mouse drag to rotate manually
- **Zoom**: Mouse wheel or +/- keys to zoom in/out

## Troubleshooting

### Common Issues

1. **"No OpenGL context" error**
   - Try running with different OpenGL settings
   - Check if your system supports OpenGL

2. **"Shader compilation failed" error**
   - Use `legacy_cube_minimal.py` instead
   - This version doesn't require shaders

3. **"PicoGL import failed" error**
   - Use `legacy_cube_minimal.py` instead
   - Or install PicoGL: `pip install picogl`

4. **Black screen or no rendering**
   - Check if your system supports OpenGL
   - Try updating graphics drivers
   - Use `legacy_cube_minimal.py` for maximum compatibility

### macOS Specific Issues

On macOS, you might encounter issues with OpenGL context creation. Try:

1. **Use the minimal version**:
   ```bash
   python legacy_cube_minimal.py
   ```

2. **Check OpenGL version**:
   ```python
   import OpenGL.GL as GL
   print(GL.glGetString(GL.GL_VERSION))
   ```

3. **Use software rendering** (if available):
   ```bash
   export MESA_GL_VERSION_OVERRIDE=3.3
   python legacy_cube_minimal.py
   ```

## Technical Details

### OpenGL Versions Used

- **`legacy_cube_minimal.py`**: OpenGL 1.x (immediate mode)
- **`legacy_cube_fixed.py`**: OpenGL 1.x/2.x (legacy VBOs)
- **`cube.py`**: OpenGL 3.3+ (modern shaders)

### Rendering Pipeline

1. **Minimal Version**: Uses immediate mode OpenGL (`glBegin`/`glEnd`)
2. **Fixed Version**: Uses `LegacyGLMesh` with legacy VBOs
3. **Original Version**: Uses `RenderWindow` with modern VAO/VBO and shaders

### Fallback Mechanisms

- **Minimal Version**: No fallback needed (uses built-in primitives)
- **Fixed Version**: Falls back to wireframe cube if mesh loading fails
- **Original Version**: No fallback (requires modern OpenGL)

## Performance Notes

- **Minimal Version**: Fastest, uses immediate mode rendering
- **Fixed Version**: Medium performance, uses legacy VBOs
- **Original Version**: Slowest, uses full shader pipeline

## Development Notes

If you need to modify these examples:

1. **For maximum compatibility**: Modify `legacy_cube_minimal.py`
2. **For PicoGL integration**: Modify `legacy_cube_fixed.py`
3. **For modern features**: Modify `cube.py`

## Comparison with Original

| Feature | Original | Legacy Fixed | Legacy Minimal |
|---------|----------|--------------|----------------|
| OpenGL Version | 3.3+ | 1.x/2.x | 1.x |
| Dependencies | PicoGL + Shaders | PicoGL | PyOpenGL only |
| Compatibility | Low | Medium | High |
| Performance | Slow | Medium | Fast |
| Features | Full | Most | Basic |

## License

These examples are part of the PicoGL project and follow the same license terms.
