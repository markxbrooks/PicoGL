"""
Simple Textured PicoGL Teapot Example

This example demonstrates how to load and render a textured teapot using
PicoGL's TextureRenderer with GLUT for maximum compatibility.

Features:
- Uses TextureRenderer for automatic texture handling
- Works with GLUT (no Qt dependencies)
- Multiple texture options
- Interactive controls

Available textures:
- resources/tu02/uvtemplate.DDS - UV template texture
- resources/tu03/uvmap.DDS - UV mapping texture
- resources/tu09/Holstein.DDS - Holstein pattern
- resources/tu10/diffuse.DDS - Diffuse texture
"""

from pathlib import Path

from picogl.renderer import MeshData
from picogl.renderer.texture import TextureRenderer
from picogl.ui.backend.glut.window.object import RenderWindow
from picogl.utils.loader.object import ObjectLoader

BASE_DIR = Path(__file__).resolve().parent
GLSL_DIR = Path(__file__).parent / "glsl" / "teapot_textured"


def main() -> None:
    """Set up the simple textured teapot object and show it."""
    print("🚀 Loading Simple Textured Teapot...")

    # Load teapot with UV coordinates
    object_file_name = str(BASE_DIR / "data" / "teapot2.obj")
    print(f"📁 Loading OBJ file: {object_file_name}")

    obj_loader = ObjectLoader(object_file_name)
    teapot_data = obj_loader.to_array_style()

    print(f"✅ Loaded teapot data:")
    print(f"   - Vertices: {len(teapot_data.vertices) // 3}")
    print(f"   - Normals: {len(teapot_data.normals) // 3}")
    print(f"   - UVs: {len(teapot_data.texcoords) // 2}")
    print(f"   - Faces: {len(teapot_data.indices) // 3}")

    # Create mesh data with UV coordinates
    data = MeshData.from_raw(
        vertices=teapot_data.vertices,
        normals=teapot_data.normals,
        uvs=teapot_data.texcoords,
        colors=(
            [[0.8, 0.8, 0.8]] * (len(teapot_data.vertices) // 3)
        ),  # Light gray base colour
    )

    # Create render window with texture support
    print("🖼️ Creating render window...")
    render_window = RenderWindow(
        width=800,
        height=600,
        title="Simple Textured Newell Teapot",
        glsl_dir=GLSL_DIR,
        base_dir=BASE_DIR,
        data=data,
        use_texture=True,  # Enable texture rendering
        texture_file="uvtemplate.tga",  # Use the UV template texture
        resource_subdir="tu02",  # Resources directory
    )

    print(f"📷 Texture file: {BASE_DIR / 'resources' / 'tu02' / 'uvtemplate.tga'}")
    print(f"✅ Texture renderer initialized")

    print("🚀 Starting simple textured teapot renderer...")
    print("   - Controls: Mouse drag to rotate, wheel to zoom")
    print("   - Texture: UV template pattern")
    print("   - Rendering: Modern OpenGL with texture mapping")
    print("   - Backend: GLUT (no Qt dependencies)")

    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    """Run the main function."""
    main()
