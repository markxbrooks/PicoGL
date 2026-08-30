# Qt Cube Renderer Examples

This directory contains Qt-based cube renderer examples for PicoGL, designed for legacy displays and systems that prefer Qt over GLUT.

## Examples

### 1. `qt_cube.py` - Full-Featured Qt Cube Renderer

**Features:**
- Uses PicoGL's `GLBase` class
- Full Qt application with controls
- Legacy OpenGL rendering
- Mouse controls for rotation and zoom
- Auto-rotation toggle
- Reset functionality
- Comprehensive UI with instructions

**Requirements:**
- PySide6 (Qt6)
- PyOpenGL
- NumPy
- PicoGL

**Usage:**
```bash
python examples/legacy_qt_cube.py
```

### 2. `qt_cube_simple.py` - Minimal Qt Cube Renderer

**Features:**
- Minimal dependencies
- Works with PySide6, PyQt5, or PyQt6
- Basic Qt OpenGL widget
- Legacy OpenGL rendering
- Mouse controls
- Simple interface

**Requirements:**
- PySide6, PyQt5, or PyQt6 (any one)
- PyOpenGL
- NumPy
- PicoGL

**Usage:**
```bash
python examples/legacy_qt_cube_simple.py
```

## Controls

Both examples support the following controls:

- **Mouse Drag (Left Button):** Manual rotation (disables auto-rotation)
- **Mouse Wheel:** Zoom in/out
- **Space:** Toggle auto-rotation on/off
- **R:** Reset view to default position
- **Escape:** Close application

## Installation

### Option 1: Full Qt Installation (Recommended)

```bash
# Install PySide6 (Qt6)
pip install PySide6

# Install other dependencies
pip install PyOpenGL PyOpenGL_accelerate numpy

# Install PicoGL (if not already installed)
pip install -e .
```

### Option 2: Minimal Qt Installation

```bash
# Install PyQt5 (lighter than PySide6)
pip install PyQt5

# Or install PyQt6
pip install PyQt6

# Install other dependencies
pip install PyOpenGL PyOpenGL_accelerate numpy

# Install PicoGL (if not already installed)
pip install -e .
```

## Troubleshooting

### Common Issues

1. **"No Qt installation found"**
   - Install one of: PySide6, PyQt5, or PyQt6
   - The simple version will try all three automatically

2. **"PyOpenGL not available"**
   - Install PyOpenGL: `pip install PyOpenGL PyOpenGL_accelerate`

3. **"PicoGL not available"**
   - Install PicoGL: `pip install -e .` (from project root)

4. **Black screen or no rendering**
   - Check if your system supports OpenGL
   - Try running with `--verbose` flag if available
   - Check console output for error messages

5. **Performance issues**
   - Reduce animation speed by modifying `rotation_speed`
   - Disable auto-rotation with Space key
   - Check if hardware acceleration is enabled

### Platform-Specific Notes

#### Windows
- Ensure you have the latest graphics drivers
- PySide6 is recommended for best compatibility
- If using PyQt5, ensure you have the correct version

#### macOS
- PySide6 works well on macOS
- May need to allow the application in Security & Privacy settings
- Legacy OpenGL support varies by macOS version

#### Linux
- Any Qt version should work
- Ensure OpenGL drivers are installed
- May need to install additional OpenGL packages

## Technical Details

### Rendering Pipeline

Both examples use legacy OpenGL (OpenGL 1.x/2.x) for maximum compatibility:

1. **Immediate Mode Rendering:** Uses `glVertexPointer` and `glColorPointer`
2. **Fixed Function Pipeline:** No shaders required
3. **Legacy Lighting:** Uses `glLightfv` and `glMaterialfv`
4. **Matrix Stack:** Uses `glMatrixMode` and `glLoadIdentity`

### Architecture

- **QtCubeRenderer/SimpleQtCubeWidget:** Main OpenGL widget
- **QtCubeWindow/SimpleQtCubeWindow:** Main application window
- **Animation Timer:** 60 FPS update loop
- **Event Handling:** Mouse and keyboard input processing

### Performance Considerations

- **Animation Timer:** 16ms interval (~60 FPS)
- **Vertex Data:** Pre-loaded into NumPy arrays
- **OpenGL State:** Minimal state changes per frame
- **Memory Usage:** Low memory footprint

## Comparison with GLUT Examples

| Feature | GLUT Examples | Qt Examples |
|---------|---------------|-------------|
| **Dependencies** | GLUT only | Qt + OpenGL |
| **Window Management** | Basic | Full Qt integration |
| **UI Controls** | None | Rich UI with buttons/labels |
| **Event Handling** | Basic | Advanced Qt events |
| **Cross-Platform** | Good | Excellent |
| **Legacy Support** | Excellent | Good |
| **Memory Usage** | Low | Medium |
| **Development** | Simple | More complex |

## Future Enhancements

Potential improvements for the Qt cube examples:

1. **Texture Support:** Add texture mapping capabilities
2. **Multiple Objects:** Render multiple cubes or other shapes
3. **Lighting Controls:** Interactive lighting adjustment
4. **Material Editor:** Real-time material property editing
5. **Export Functionality:** Save rendered frames or animations
6. **Configuration Dialog:** Settings for rendering options
7. **Performance Monitor:** FPS counter and performance metrics

## Contributing

To contribute to the Qt cube examples:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## License

These examples are part of the PicoGL project and follow the same license terms.
