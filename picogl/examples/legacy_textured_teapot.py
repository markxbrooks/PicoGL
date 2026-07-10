"""
Legacy Textured PicoGL Teapot Example

This example demonstrates how to load and render a textured teapot using
legacy OpenGL (OpenGL 1.x/2.x) for maximum compatibility.

Features:
- Uses LegacyGLMesh for rendering
- Legacy OpenGL texture mapping
- Works on systems without modern shader support
- Interactive controls for rotation and zoom
- Multiple texture options

Available textures:
- resources/tu02/uvtemplate.DDS - UV template texture
- resources/tu03/uvmap.DDS - UV mapping texture
- resources/tu09/Holstein.DDS - Holstein pattern
- resources/tu10/diffuse.DDS - Diffuse texture
"""

import sys
from pathlib import Path
from typing import Optional

from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.gl.mode import GLMode
from picogl.backend.gl.api import gl_bind_texture
from picogl.backend.gl.api.clear import gl_clear
from picogl.backend.gl.api.enable import gl_disable, gl_enable
from picogl.backend.gl.api.glu import glu_look_at
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.texture.gltexture import GLTexture
from picogl.ui.backend.qt.legacy.renderer import LegacyQtObjectRenderer
from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QPushButton,
                               QVBoxLayout, QWidget)

# OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print("❌ Error: PyOpenGL not available")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.utils.loader.object import ObjectLoader
from picogl.utils.loader.texture import TextureLoader

BASE_DIR = Path(__file__).resolve().parent


class LegacyTexturedTeapotRenderer(LegacyQtObjectRenderer):
    """
    Legacy textured teapot renderer using OpenGL 1.x/2.x

    This class provides a textured teapot renderer that works on
    systems with limited OpenGL support.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the textured teapot renderer"""
        super().__init__()

        # Teapot data
        self.texture_id = None
        self.texture_loader = None
        # Texture options (using TGA where available, DDS as fallback)
        self.texture_options = {
            "UV Template": ("tu02", "uvtemplate.tga"),
            "UV Map": ("tu03", "uvmap.DDS"),
            "Holstein": ("tu09", "Holstein.DDS"),
            "Diffuse": ("tu10", "diffuse.DDS"),
            "AK-47": ("tu05", "AK-47_01_D_Fix.tga"),
        }
        self.current_texture = "UV Template"

        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def load_teapot_data(self):
        """Load teapot data with UV coordinates"""
        print("📁 Loading teapot data...")

        object_file_name = str(BASE_DIR / "data" / "teapot2.obj")
        obj_loader = ObjectLoader(object_file_name)
        teapot_data = obj_loader.to_array_style()

        print(f"✅ Loaded teapot data:")
        print(f"   - Vertices: {len(teapot_data.vertices) // 3}")
        print(f"   - Normals: {len(teapot_data.normals) // 3}")
        print(f"   - UVs: {len(teapot_data.texcoords) // 2}")
        print(f"   - Faces: {len(teapot_data.indices) // 3}")

        # Create mesh data
        self.mesh_data = MeshData.from_raw(
            vertices=teapot_data.vertices,
            normals=teapot_data.normals,
            uvs=teapot_data.texcoords,
            indices=teapot_data.indices,
            colors=([[0.8, 0.8, 0.8]] * (len(teapot_data.vertices) // 3)),
        )

        return self.mesh_data

    def load_texture(self, texture_name: str = None):
        """Load texture from resources"""
        if texture_name is None:
            texture_name = self.current_texture

        if texture_name not in self.texture_options:
            print(f"❌ Unknown texture: {texture_name}")
            return False

        subdir, filename = self.texture_options[texture_name]
        texture_path = BASE_DIR / "resources" / subdir / filename

        print(f"🎨 Loading texture: {texture_path}")

        try:
            self.texture_loader = TextureLoader(str(texture_path))
            self.texture_id = self.texture_loader.texture_gl_id

            if self.texture_id is not None:
                print(f"✅ Texture loaded successfully (ID: {self.texture_id})")
                return True
            else:
                print(f"❌ Failed to load texture: {texture_path}")
                return False

        except Exception as e:
            print(f"❌ Error loading texture: {e}")
            return False

    def initializeGL(self):
        """Initialize OpenGL state for textured teapot rendering"""
        super().initializeGL()
        self.initialize_state()
        self.initialize_lighting()
        self.initialize_materials()

        # Load teapot data
        self.load_teapot_data()

        # Load texture
        self.load_texture()

        # Create and upload mesh data
        self.initialize()

    def initialize_state(self):
        """Set up basic OpenGL state"""
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        gl_enable(GL_DEPTH_TEST)
        gl_enable(GL_TEXTURE_2D)

    def initialize(self):
        """Initialize mesh data and upload to GPU"""
        if self._initialized:
            return

        if self.mesh_data is not None:
            self.gl_data = LegacyGLMesh.from_mesh_data(mesh=self.mesh_data)
            self.gl_data.upload()
            self._initialized = True
            print("✅ Legacy Textured Teapot Renderer initialized")

    def paintGL(self):
        """Render the textured teapot scene"""
        # Clear buffers
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)

        # Set up modelview matrix
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)
        gl_load_identity()

        # Position camera
        glu_look_at(0, 0, self.zoom, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        gl_rotate_f(self.rotation_x, 1, 0, 0)
        gl_rotate_f(self.rotation_y, 0, 1, 0)

        # Bind texture if available
        if self.texture_id is not None:
            gl_bind_texture(GLTexture.TEXTURE_2D, self.texture_id)
            gl_enable(GLTexture.TEXTURE_2D)
        else:
            gl_disable(GLTexture.TEXTURE_2D)

        # Draw the teapot using LegacyGLMesh
        self.draw()

    def draw(self):
        """Draw the teapot using LegacyGLMesh"""
        if self.gl_data is not None:
            self.gl_data.draw()

    def change_texture(self, texture_name: str):
        """Change the current texture"""
        if texture_name in self.texture_options:
            self.current_texture = texture_name
            self.load_texture(texture_name)
            print(f"🔄 Changed texture to: {texture_name}")


class LegacyTexturedTeapotWindow(LegacyQtObjectWindow):
    """
    Main window for the legacy textured teapot renderer
    """

    def __init__(self):
        super().__init__(parent=self, gl_mode=GLMode.LEGACY)
        self.setWindowTitle("PicoGL Legacy Textured Teapot - OpenGL 1.x/2.x")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        self.set_layout(layout)

    def set_layout(self, layout):
        # Create info label
        info_label = QLabel(
            """
            <h3>PicoGL Legacy Textured Teapot</h3>
            <p><b>Controls:</b></p>
            <ul>
            <li><b>Mouse Drag:</b> Manual rotation (disables auto-rotation)</li>
            <li><b>Mouse Wheel:</b> Zoom in/out</li>
            <li><b>Space:</b> Toggle auto-rotation</li>
            <li><b>R:</b> Reset view</li>
            <li><b>Escape:</b> Close application</li>
            </ul>
            <p><b>Rendering:</b> Legacy OpenGL with texture mapping</p>
            """
        )
        info_label.setMaximumHeight(180)
        layout.addWidget(info_label)

        # Create texture selection
        texture_layout = QVBoxLayout()
        texture_label = QLabel("Select Texture:")
        texture_layout.addWidget(texture_label)

        self.texture_combo = QComboBox()
        self.texture_combo.addItems(
            ["UV Template", "UV Map", "Holstein", "Diffuse", "AK-47"]
        )
        self.texture_combo.currentTextChanged.connect(self.change_texture)
        texture_layout.addWidget(self.texture_combo)

        layout.addLayout(texture_layout)

        # Create OpenGL widget
        self.gl_widget = LegacyTexturedTeapotRenderer()
        layout.addWidget(self.gl_widget)

        # Create control buttons
        button_layout = QVBoxLayout()

        auto_rotate_btn = QPushButton("Toggle Auto-Rotation")
        auto_rotate_btn.clicked.connect(self.toggle_auto_rotate)
        button_layout.addWidget(auto_rotate_btn)

        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(self.reset_view)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

        # Set focus to OpenGL widget for keyboard input
        self.gl_widget.setFocusPolicy(Qt.StrongFocus)
        self.gl_widget.setFocus()

    def change_texture(self, texture_name: str):
        """Change the current texture"""
        self.gl_widget.change_texture(texture_name)


def main():
    """Main function to run the legacy textured teapot renderer"""
    print("🚀 Starting PicoGL Legacy Textured Teapot...")

    # Check for Qt availability
    try:
        app = QApplication(sys.argv)
    except ImportError as e:
        print("❌ Error: PySide6 not available")
        print("Please install PySide6: pip install PySide6")
        return 1

    # Create and show window
    window = LegacyTexturedTeapotWindow()
    window.show()

    print("✅ Legacy Textured Teapot started successfully!")
    print("   - Window: 800x600")
    print("   - Rendering: Legacy OpenGL with texture mapping")
    print("   - Controls: Mouse drag, wheel, keyboard, texture selection")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    """Run the main function."""
    main()
