# Textured Teapot Examples

This directory contains examples demonstrating how to add textures to the classic Newell teapot using PicoGL.

## Examples

### 1. `textured_teapot.py` - Modern Textured Teapot

**Features:**
- Uses modern OpenGL shaders with texture support
- TextureRenderer for automatic texture loading
- GLUT-based window (no Qt dependencies)
- UV coordinate support from teapot2.obj

**Requirements:**
- PyOpenGL
- NumPy
- PicoGL
- Modern OpenGL support

**Usage:**
```bash
python examples/textured_teapot.py
```

### 2. `legacy_textured_teapot.py` - Legacy Textured Teapot

**Features:**
- Uses legacy OpenGL (OpenGL 1.x/2.x)
- Qt-based interface with texture selection
- Works on systems without modern shader support
- Interactive texture switching
- Mouse and keyboard controls

**Requirements:**
- PySide6 (Qt6)
- PyOpenGL
- NumPy
- PicoGL

**Usage:**
```bash
python examples/legacy_textured_teapot.py
```

### 3. `simple_textured_teapot.py` - Simple Textured Teapot

**Features:**
- Uses TextureRenderer with GLUT
- No Qt dependencies
- Modern OpenGL with texture mapping
- Simple and lightweight

**Requirements:**
- PyOpenGL
- NumPy
- PicoGL
- Modern OpenGL support

**Usage:**
```bash
python examples/simple_textured_teapot.py
```

## Available Textures

The examples use textures from the `resources/` directory:

| Texture | File | Description |
|---------|------|-------------|
| **UV Template** | `tu02/uvtemplate.tga` | UV coordinate visualization (TGA format) |
| **UV Map** | `tu03/uvmap.DDS` | UV mapping pattern (DDS format) |
| **Holstein** | `tu09/Holstein.DDS` | Holstein cow pattern (DDS format) |
| **Diffuse** | `tu10/diffuse.DDS` | Diffuse material texture (DDS format) |
| **AK-47** | `tu05/AK-47_01_D_Fix.tga` | AK-47 weapon texture (TGA format) |

## Shaders

### Modern Shaders (`glsl/teapot_textured/`)

- **`vertex.glsl`**: Vertex shader with UV coordinate support
- **`fragment.glsl`**: Fragment shader with texture sampling and lighting

**Key Features:**
- UV coordinate interpolation
- Texture sampling with `sampler2D`
- Mixing texture with vertex colors
- Phong lighting model
- Configurable texture mixing

## Controls

### All Examples
- **Mouse Drag (Left Button):** Manual rotation
- **Mouse Wheel:** Zoom in/out
- **Space:** Toggle auto-rotation (where applicable)
- **R:** Reset view (where applicable)
- **Escape:** Close application

### Legacy Textured Teapot (Qt version)
- **Texture ComboBox:** Switch between different textures
- **Toggle Auto-Rotation Button:** Enable/disable automatic rotation
- **Reset View Button:** Reset camera to default position

## Technical Details

### UV Coordinates

The examples use `teapot2.obj` which includes UV coordinates:
- **Format:** OBJ file with `vt` (texture coordinate) lines
- **Mapping:** Spherical UV mapping for the teapot
- **Usage:** Passed to shaders as `layout(location = 3) in vec2 vertexUV`

### Texture Loading

Textures are loaded using PicoGL's `TextureLoader`:
- **Supported Formats:** DDS, TGA, PNG, BMP
- **Automatic Format Detection:** Based on file extension
- **GPU Upload:** Textures are uploaded to GPU during initialization

### Rendering Pipeline

1. **Data Loading:** Load OBJ file with UV coordinates
2. **Mesh Creation:** Create `MeshData` with vertices, normals, UVs, colors
3. **Texture Loading:** Load texture using `TextureLoader`
4. **Shader Compilation:** Compile vertex and fragment shaders
5. **Rendering:** Draw textured mesh with lighting

## Troubleshooting

### Common Issues

1. **"No UV coordinates found"**
   - Ensure you're using `teapot2.obj` (not `teapot.obj`)
   - Check that the OBJ file contains `vt` lines

2. **"Texture not found"**
   - Verify texture files exist in `resources/` directory
   - Check file paths and extensions

3. **"DDS textures not loading"**
   - DDS loader may not work properly on all systems
   - Use TGA files instead: `uvtemplate.tga`, `AK-47_01_D_Fix.tga`
   - TGA files are more reliable and widely supported

4. **"Shader compilation failed"**
   - Ensure your system supports OpenGL 3.3+
   - Check shader syntax and version compatibility

5. **"Legacy version not working"**
   - Install PySide6: `pip install PySide6`
   - Check OpenGL driver compatibility

### Performance Tips

1. **Texture Size:** Use appropriate texture sizes (512x512 or 1024x1024)
2. **Format:** TGA files are more reliable than DDS on many systems
3. **Compression:** DDS provides better compression but may not work on all systems
4. **Mipmaps:** Enable mipmap generation for better quality
5. **Fallback:** Use TGA as primary format, DDS as fallback for better compatibility

## Customization

### Adding New Textures

1. **Add texture file** to `resources/` directory
2. **Update texture options** in the code:
   ```python
   self.texture_options = {
       "Your Texture": ("subdir", "filename.ext"),
       # ... existing textures
   }
   ```

### Modifying Shaders

1. **Edit shader files** in `glsl/teapot_textured/`
2. **Add new uniforms** for custom effects
3. **Modify lighting model** in fragment shader
4. **Add texture effects** like normal mapping

### Changing Teapot Model

1. **Use different OBJ file** with UV coordinates
2. **Update file path** in the loader
3. **Adjust scaling/positioning** as needed
4. **Verify UV mapping** works with new model

## Examples Gallery

### UV Template Texture
- Shows UV coordinate mapping
- Useful for debugging UV issues
- Color-coded coordinate visualization

### Holstein Pattern
- Classic cow pattern texture
- Good for testing texture tiling
- High contrast for visibility

### Diffuse Texture
- Realistic material appearance
- Subtle color variations
- Professional look

## Future Enhancements

Potential improvements for the textured teapot examples:

1. **Normal Mapping:** Add normal map support
2. **Specular Mapping:** Add specular map support
3. **Multiple Textures:** Support for multiple texture layers
4. **Animation:** Animated texture effects
5. **PBR Materials:** Physically-based rendering
6. **Texture Atlases:** Support for texture atlases
7. **Dynamic Loading:** Runtime texture switching
8. **Texture Compression:** Automatic texture compression

## Contributing

To contribute to the textured teapot examples:

1. Fork the repository
2. Create a feature branch
3. Add your texture or shader improvements
4. Test on multiple platforms
5. Submit a pull request

## License

These examples are part of the PicoGL project and follow the same license terms.
