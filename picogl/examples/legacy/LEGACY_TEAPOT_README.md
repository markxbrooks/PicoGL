# Legacy Teapot Examples for PicoGL

This directory contains several teapot rendering examples designed to work on systems with limited OpenGL support, including older macOS systems.

## Examples Overview

### 1. `legacy_teapot.py` (Original - May not work on all systems)
- Uses modern `ObjectRenderer` with OpenGL 3.3+ shaders
- Requires shader files and modern OpenGL support
- May fail on older macOS systems or systems without shader support

### 2. `legacy_teapot_fixed.py` (Recommended for OBJ file support)
- Uses `LegacyGLMesh` for OpenGL 1.x/2.x compatibility
- Loads teapot data from OBJ file
- Falls back to wireframe teapot if OBJ file not found
- Works on systems without modern shader support

### 3. `legacy_teapot_simple.py` (Recommended for maximum compatibility)
- Uses only built-in OpenGL primitives (`glutSolidTeapot`)
- No external files required
- Maximum compatibility with older systems
- Works on any system with basic OpenGL support

### 4. `legacy_teapot_minimal.py` (Ultimate fallback)
- Minimal dependencies (only PyOpenGL)
- No PicoGL library required
- Maximum compatibility with older systems
- Use this if other versions fail

## System Requirements

### Minimum Requirements
- Python 3.7+
- PyOpenGL
- GLUT (usually included with PyOpenGL)
- Basic OpenGL 1.x support

### Recommended for `legacy_teapot_fixed.py`
- Python 3.7+
- PyOpenGL
- GLUT
- NumPy
- PicoGL library
- `data/teapot.obj` file (optional)

## Installation

```bash
# Install required packages
pip install PyOpenGL PyOpenGL_accelerate numpy

# If using the fixed version with OBJ support
pip install picogl  # Install PicoGL library
```

## Usage

### Minimal Teapot (Ultimate Fallback)
```bash
cd examples
python legacy_teapot_minimal.py
```

### Simple Teapot (Maximum Compatibility)
```bash
cd examples
python legacy_teapot_simple.py
```

### Fixed Teapot with OBJ Support
```bash
cd examples
python legacy_teapot_fixed.py
```

### Original Teapot (Modern OpenGL)
```bash
cd examples
python legacy_teapot.py
```

## Controls

All examples support the following controls:

- **Mouse**: Rotate view
- **Mouse Wheel**: Zoom in/out
- **R**: Reset rotation
- **W**: Toggle wireframe mode
- **F**: Fill mode
- **ESC**: Exit

Additional controls for `legacy_teapot_simple.py`:
- **N**: Toggle normals display
- **+/-**: Zoom in/out
- **Space**: Toggle auto-rotation

## Troubleshooting

### Common Issues

1. **"No OpenGL context" error**
   - Try running with different OpenGL settings
   - Check if your system supports OpenGL

2. **"Shader compilation failed" error**
   - Use `legacy_teapot_simple.py` instead
   - This version doesn't require shaders

3. **"OBJ file not found" error**
   - The `legacy_teapot_fixed.py` will fall back to wireframe teapot
   - Or use `legacy_teapot_simple.py` which doesn't need OBJ files

4. **Black screen or no rendering**
   - Check if your system supports OpenGL
   - Try updating graphics drivers
   - Use `legacy_teapot_simple.py` for maximum compatibility

### macOS Specific Issues

On macOS, you might encounter issues with OpenGL context creation. Try:

1. **Use the simple version**:
   ```bash
   python legacy_teapot_simple.py
   ```

2. **Check OpenGL version**:
   ```python
   import OpenGL.GL as GL
   print(GL.glGetString(GL.GL_VERSION))
   ```

3. **Use software rendering** (if available):
   ```bash
   export MESA_GL_VERSION_OVERRIDE=3.3
   python legacy_teapot_simple.py
   ```

## Technical Details

### OpenGL Versions Used

- **`legacy_teapot_simple.py`**: OpenGL 1.x (immediate mode)
- **`legacy_teapot_fixed.py`**: OpenGL 1.x/2.x (legacy VBOs)
- **`legacy_teapot.py`**: OpenGL 3.3+ (modern shaders)

### Rendering Pipeline

1. **Simple Version**: Uses `glutSolidTeapot()` - built-in OpenGL primitive
2. **Fixed Version**: Uses `LegacyGLMesh` - custom mesh with legacy VBOs
3. **Original Version**: Uses `ObjectRenderer` - modern VAO/VBO with shaders

### Fallback Mechanisms

- **Simple Version**: No fallback needed (uses built-in primitives)
- **Fixed Version**: Falls back to wireframe teapot if OBJ loading fails
- **Original Version**: No fallback (requires modern OpenGL)

## Performance Notes

- **Simple Version**: Fastest, uses hardware-optimized primitives
- **Fixed Version**: Medium performance, custom mesh rendering
- **Original Version**: Slowest, full shader pipeline

## Development Notes

If you need to modify these examples:

1. **For maximum compatibility**: Modify `legacy_teapot_simple.py`
2. **For custom meshes**: Modify `legacy_teapot_fixed.py`
3. **For modern features**: Modify `legacy_teapot.py`

## License

These examples are part of the PicoGL project and follow the same license terms.
