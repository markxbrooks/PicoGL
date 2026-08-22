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

from picogl.backend.gl.api.clear import gl_clear, gl_clear_rgba_color
from picogl.backend.gl.api.color import gl_color_3f, gl_color_material
from picogl.backend.gl.api.enable import gl_disable, gl_enable
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace, GLPipelineCapability)
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode
from picogl.backend.glut import (GLUTDisplayMode, GLUTMouseButton,
                                 GLUTMouseState, glut_create_window,
                                 glut_display_func, glut_init,
                                 glut_init_display_mode, glut_init_window_size,
                                 glut_keyboard_func, glut_main_loop,
                                 glut_motion_func, glut_mouse_func,
                                 glut_post_redisplay, glut_reshape_func,
                                 glut_swap_buffers, glut_wire_teapot)
from picogl.backend.legacy.core.camera.legacy_camera import LegacyCamera
from picogl.backend.legacy.core.camera.projection_state import (
    GLUProjectionState)
from picogl.backend.state import GLViewport
from picogl.core.camera import ProjectionConfig
from picogl.core.polygon.mode import (set_polygon_mode_fill,
                                      set_polygon_mode_line)
from picogl.core.rgbcolor import RGBAColor
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.legacy_mesh_loader import load_legacy_mesh


class LegacyRenderer:
    """GLUT-based fixed-function OpenGL renderer."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy Renderer",
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.mesh: LegacyGLMesh | None = None

        self.viewport = GLViewport(width=width, height=height)
        self.projection_config = ProjectionConfig(near=0.1, far=100.0)
        self.projection = GLUProjectionState()
        self.camera = LegacyCamera(distance=5.0)

    def init_glut(self) -> None:
        """Initialize GLUT window and callbacks."""
        glut_init()
        glut_init_display_mode(
            GLUTDisplayMode.RGBA | GLUTDisplayMode.DOUBLE | GLUTDisplayMode.DEPTH
        )
        glut_init_window_size(self.width, self.height)
        glut_create_window(self.title)

        glut_display_func(self.render)
        glut_reshape_func(self.reshape)
        glut_keyboard_func(self.keyboard)
        glut_mouse_func(self.mouse)
        glut_motion_func(self.motion)

    def init_gl(self) -> None:
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

    def render(self) -> None:
        """Render the scene."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        self.camera.apply()

        if self.mesh is not None:
            try:
                self.mesh.draw()
            except Exception as e:
                print(f"Error drawing mesh: {e}")
                self.draw_fallback_teapot()
        else:
            self.draw_fallback_teapot()

        glut_swap_buffers()

    def draw_fallback_teapot(self) -> None:
        """Draw a simple wireframe teapot as fallback."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        gl_color_3f((1.0, 0.0, 0.0))  # Red wireframe
        set_polygon_mode_line()
        glut_wire_teapot(1.0)
        set_polygon_mode_fill()
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def reshape(self, width: int, height: int) -> None:
        """Handle GLUT window resize."""
        self.width = width
        self.height = height
        self.viewport.width = width
        self.viewport.height = height
        self.viewport.apply()
        self.projection.apply(self.projection_config.with_size(width, height))

    def keyboard(self, key, x, y) -> None:
        """Keyboard callback."""
        del x, y
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.camera.rotation.reset()
        elif key == b"w":  # Wireframe mode
            set_polygon_mode_line()
        elif key == b"f":  # Fill mode
            set_polygon_mode_fill()
        glut_post_redisplay()

    def mouse(self, button, state, x, y) -> None:
        """Mouse callback."""
        if button == GLUTMouseButton.LEFT:
            if state == GLUTMouseState.DOWN:
                self.camera.rotation.press(x, y)
            else:
                self.camera.rotation.release()
        elif button == GLUTMouseButton.WHEEL_UP:
            self.camera.distance = max(1.0, self.camera.distance - 0.5)
        elif button == GLUTMouseButton.WHEEL_DOWN:
            self.camera.distance = min(20.0, self.camera.distance + 0.5)
        glut_post_redisplay()

    def motion(self, x, y) -> None:
        """Mouse motion callback."""
        if self.camera.rotation.drag(x, y) is None:
            return
        self.camera.rotation.clamp_x()
        glut_post_redisplay()

    def run(self) -> None:
        """Run the application main loop."""
        self.init_glut()
        self.init_gl()

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Wireframe mode")
        print("   F: Fill mode")
        print("   ESC: Exit")
        print("\n🚀 Starting legacy teapot renderer...")

        glut_main_loop()


def main() -> None:
    """Main function."""
    try:
        base_dir = Path(__file__).resolve().parent
        obj_file_path = base_dir / "data" / "teapot.obj"
        renderer = LegacyRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Teapot (OpenGL 1.x/2.x Compatible)",
        )

        if not obj_file_path.exists():
            print(f"❌ Teapot OBJ file not found at {obj_file_path}")
            print("   Using fallback wireframe teapot instead.")
        else:
            try:
                renderer.mesh = load_legacy_mesh(obj_file_path)
                print(f"✅ Loaded teapot from {obj_file_path}")
            except Exception as e:
                print(f"❌ Error loading teapot data: {e}")
                print("   Using fallback wireframe teapot instead.")

        renderer.run()
    except Exception as e:
        print(f"❌ Error running legacy teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")


if __name__ == "__main__":
    main()
