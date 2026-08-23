"""Legacy PicoGL Teapot - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

from __future__ import annotations


from pathlib import Path

from decologr import logger as log
from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.scoped import disabled
from picogl.backend.glut import glut_wire_teapot
from picogl.backend.legacy.core.renderer import LegacyRenderer
from picogl.core.polygon.mode import set_polygon_mode_fill, set_polygon_mode_line
from picogl.core.rgbcolor import RGBColor
from picogl.polygon.mode import polygon_mode
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.legacy_mesh_loader import load_legacy_mesh


class LegacyTeapotRenderer(LegacyRenderer):
    """GLUT teapot renderer with LegacyGLMesh and wireframe fallback."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy Teapot Renderer",
    ) -> None:
        super().__init__(width=width, height=height, title=title)
        self.mesh: LegacyGLMesh | None = None

    def draw_scene(self) -> None:
        if self.mesh is not None:
            try:
                self.mesh.draw()
                return
            except Exception as exc:
                print(f"Error drawing mesh: {exc}")
        self.draw_fallback_teapot()

    def draw_fallback_teapot(self) -> None:
        """Draw a simple wireframe teapot as fallback."""
        with disabled(GLFixedFunctionCapability.LIGHTING):
            with polygon_mode(GLFillMode.LINE):
                gl_color_rgb(RGBColor(r=1.0, g=0.0, b=0.0))
                glut_wire_teapot(1.0)

    def handle_key(self, key: bytes) -> None:
        if key == b"w":
            set_polygon_mode_line()
        elif key == b"f":
            set_polygon_mode_fill()

    def startup_message(self) -> None:
        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Wireframe mode")
        print("   F: Fill mode")
        print("   ESC: Exit")
        print("\n🚀 Starting legacy teapot renderer...")


def main() -> None:
    """Main function."""
    try:
        base_dir = Path(__file__).resolve().parent
        obj_file_path = base_dir / "data" / "teapot.obj"
        renderer = LegacyTeapotRenderer(
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
                log.message(f"✅ Loaded teapot from {obj_file_path}")
            except Exception as exc:
                print(f"❌ Error loading teapot data: {exc}")
                print("   Using fallback wireframe teapot instead.")

        renderer.run()
    except Exception as exc:
        print(f"❌ Error running legacy teapot renderer: {exc}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")


if __name__ == "__main__":
    main()
