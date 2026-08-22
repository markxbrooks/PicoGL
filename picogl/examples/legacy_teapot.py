"""Legacy PicoGL Teapot - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np

from picogl.backend.gl.api.clear import gl_clear, gl_clear_rgba_color
from picogl.backend.gl.api.color import gl_color_3f, gl_color_material
from picogl.backend.gl.api.enable import gl_disable, gl_enable
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.rotate import gl_rotate_f
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace, GLPipelineCapability)
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity, gl_viewport
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.backend.glu.lookat import glu_look_at
from picogl.backend.glu.perspective import glu_perspective
from picogl.backend.glut import (GLUTDisplayMode, GLUTMouseButton,
                                 GLUTMouseState, glut_create_window,
                                 glut_display_func, glut_init,
                                 glut_init_display_mode, glut_init_window_size,
                                 glut_keyboard_func, glut_main_loop,
                                 glut_motion_func, glut_mouse_func,
                                 glut_post_redisplay, glut_reshape_func,
                                 glut_swap_buffers, glut_wire_teapot)
from picogl.core.polygon.mode import (set_polygon_mode_fill,
                                      set_polygon_mode_line)
from picogl.core.rgbcolor import RGBAColor
from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.ui.backend.glut.mouse import RotationInteraction
from picogl.utils.loader.object import ObjectLoader


class LegacyRenderer:
    """Legacy teapot renderer using immediate mode OpenGL."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy Renderer",
        object_file_name: Optional[str | Path] = None,
    ):
        self.width = width
        self.height = height
        self.title = title
        self.mesh = None
        self.rotation = RotationInteraction()
        self.zoom_distance = 5.0
        self.object_file_name = (
            Path(object_file_name) if object_file_name is not None else None
        )

    def init_glut(self):
        """Initialize GLUT window."""
        glut_init()
        glut_init_display_mode(
            GLUTDisplayMode.RGBA | GLUTDisplayMode.DOUBLE | GLUTDisplayMode.DEPTH
        )
        glut_init_window_size(self.width, self.height)
        glut_create_window(self.title)

        # Set callbacks
        glut_display_func(self.display)
        glut_reshape_func(self.reshape)
        glut_keyboard_func(self.keyboard)
        glut_mouse_func(self.mouse)
        glut_motion_func(self.motion)

    def init_gl(self):
        """Initialize OpenGL state."""
        gl_clear_rgba_color(RGBAColor(0.1, 0.1, 0.2, 1.0))
        gl_enable(GLPipelineCapability.DEPTH_TEST)
        gl_enable(GLFixedFunctionCapability.LIGHTING)
        gl_enable(GLFixedFunctionCapability.LIGHT0)
        gl_enable(GLCapability.COLOR_MATERIAL)
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )
        gl_legacy_lighting()

    def load_object_data(self, obj_file_path):
        """Load teapot data from OBJ file."""
        try:
            obj_loader = ObjectLoader(obj_file_path)
            object_data = obj_loader.to_array_style()

            # Create mesh data
            mesh_data = MeshData.from_raw(
                vertices=object_data.vertices,
                normals=object_data.normals,
                colors=([[1.0, 0.0, 0.0]] * (len(object_data.vertices) // 3)),
            )

            # Create legacy mesh
            self.mesh = LegacyGLMesh(
                vertices=mesh_data.vertices.reshape(-1, 3),
                faces=np.arange(len(mesh_data.vertices) // 3).reshape(-1, 3),
                colors=(
                    mesh_data.colors.reshape(-1, 3)
                    if mesh_data.colors is not None
                    else None
                ),
                normals=(
                    mesh_data.normals.reshape(-1, 3)
                    if mesh_data.normals is not None
                    else None
                ),
            )

            # Upload mesh to GPU
            self.mesh.upload()
            print(f"✅ Loaded teapot with {len(object_data.vertices) // 3} vertices")
            return True

        except Exception as e:
            print(f"❌ Error loading teapot data: {e}")
            return False

    def display(self):
        """Display callback - render the scene."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        gl_load_identity()

        # Set up camera
        glu_look_at(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        gl_rotate_f(self.rotation.x, 1, 0, 0)
        gl_rotate_f(self.rotation.y, 0, 1, 0)

        # Draw the teapot
        if self.mesh:
            try:
                self.mesh.draw()
            except Exception as e:
                print(f"Error drawing mesh: {e}")
                self.draw_fallback_teapot()
        else:
            self.draw_fallback_teapot()

        glut_swap_buffers()

    def draw_fallback_teapot(self):
        """Draw a simple wireframe teapot as fallback."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        gl_color_3f((1.0, 0.0, 0.0))  # Red wireframe
        set_polygon_mode_line()
        glut_wire_teapot(1.0)
        set_polygon_mode_fill()
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        gl_viewport(0, 0, width, height)
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        glu_perspective(45.0, float(width) / float(height), 0.1, 100.0)
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    def keyboard(self, key, x, y):
        """Keyboard callback."""
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.rotation.reset()
        elif key == b"w":  # Wireframe mode
            set_polygon_mode_line()
        elif key == b"f":  # Fill mode
            set_polygon_mode_fill()
        glut_post_redisplay()

    def mouse(self, button, state, x, y):
        """Mouse callback."""
        if button == GLUTMouseButton.LEFT:
            if state == GLUTMouseState.DOWN:
                self.rotation.press(x, y)
            else:
                self.rotation.release()
        elif button == 3:  # Mouse wheel up
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif button == 4:  # Mouse wheel down
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        glut_post_redisplay()

    def motion(self, x, y):
        """Mouse motion callback."""
        if self.rotation.drag(x, y) is None:
            return
        self.rotation.clamp_x()
        glut_post_redisplay()

    def run(self):
        """Run the application."""
        self.init_glut()
        self.init_gl()

        if self.object_file_name is None or not self.object_file_name.exists():
            path = self.object_file_name or "(none)"
            print(f"❌ Teapot OBJ file not found at {path}")
            print("   Using fallback wireframe teapot instead.")
        elif not self.load_object_data(str(self.object_file_name)):
            print("   Using fallback wireframe teapot instead.")

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Wireframe mode")
        print("   F: Fill mode")
        print("   ESC: Exit")
        print("\n🚀 Starting legacy teapot renderer...")

        glut_main_loop()


def main():
    """Main function."""
    try:
        base_dir = Path(__file__).resolve().parent
        obj_file_path = base_dir / "data" / "teapot.obj"
        renderer = LegacyRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Teapot (OpenGL 1.x/2.x Compatible)",
            object_file_name=obj_file_path,
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running legacy teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")


if __name__ == "__main__":
    main()
