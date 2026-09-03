"""Legacy PicoGL Teapot - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow ``python path/to/legacy_teapot.py`` without installing picogl.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL and then
# fail on glutDisplayFunc with "Attempt to retrieve context when no valid context".
# Must be set before any OpenGL import (including via picogl).
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401
from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.api.enable import gl_disable
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace)
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import GLCapability, GLFillMode
from picogl.backend.gl.state.scoped import gl_disabled
from picogl.backend.glut import glut_wire_teapot
from picogl.backend.legacy.core.renderer import LegacyRenderer
from picogl.core.polygon.mode import (set_polygon_mode_fill,
                                      set_polygon_mode_line)
from picogl.core.rgbcolor import RGBAColor, RGBColor
from picogl.polygon.mode import gl_polygon_mode_context
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.legacy_mesh_loader import load_legacy_mesh

# Classic ceramic/porcelain Phong response for the Newell teapot.
TEAPOT_PHONG_MATERIAL = PhongMaterial(
    ambient=RGBAColor(0.22, 0.20, 0.18, 1.0),
    diffuse=RGBAColor(0.82, 0.72, 0.62, 1.0),
    specular=RGBAColor(0.95, 0.95, 0.95, 1.0),
    shininess=64.0,
)


class LegacyTeapotRenderer(LegacyRenderer):
    """GLUT teapot renderer with LegacyGLMesh, PhongMaterial, and wireframe fallback."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Legacy Teapot Renderer",
        material: PhongMaterial | None = None,
    ) -> None:
        super().__init__(width=width, height=height, title=title)
        self.mesh: LegacyGLMesh | None = None
        self.material = material if material is not None else TEAPOT_PHONG_MATERIAL

    def init_gl(self) -> None:
        """Initialize GL state, apply PhongMaterial, and upload mesh once a context exists."""
        super().init_gl()
        # COLOR_MATERIAL would let vertex colours override ambient/diffuse.
        gl_disable(GLCapability.COLOR_MATERIAL)
        self.material.apply(GLMaterialFace.FRONT_AND_BACK)
        if self.mesh is not None and getattr(self.mesh, "vao", None) is None:
            self.mesh.upload()

    def draw_scene(self) -> None:
        if self.mesh is not None:
            try:
                if getattr(self.mesh, "vao", None) is None:
                    self.mesh.upload()
                self.material.apply(GLMaterialFace.FRONT_AND_BACK)
                with gl_disabled(GLCapability.COLOR_MATERIAL):
                    self.mesh.draw()
                return
            except Exception as exc:
                print(f"Error drawing mesh: {exc}")
        self.draw_fallback_teapot()

    def draw_fallback_teapot(self) -> None:
        """Draw a simple wireframe teapot as fallback."""
        with gl_disabled(GLFixedFunctionCapability.LIGHTING):
            with gl_polygon_mode_context(GLFillMode.LINE):
                gl_color_rgb(RGBColor(1.0, 0.0, 0.0))
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
        print(
            f"   PhongMaterial shininess={self.material.shininess:.0f} "
            f"(COLOR_MATERIAL disabled for lit mesh)"
        )


def main() -> None:
    """Main function."""
    if os.environ.get("DISPLAY") is None and os.name != "nt":
        print("❌ No display available. This requires a graphical environment.")
        sys.exit(1)

    try:
        base_dir = Path(__file__).resolve().parent
        obj_path = base_dir / "data" / "teapot.obj"
        renderer = LegacyTeapotRenderer(
            width=800,
            height=600,
            title="Legacy PicoGL Teapot (OpenGL 1.x/2.x Compatible)",
            material=TEAPOT_PHONG_MATERIAL,
        )

        if not obj_path.exists():
            print(f"❌ Teapot OBJ file not found at {obj_path}")
            print("   Using fallback wireframe teapot instead.")
        else:
            try:
                # CPU load only; GPU upload happens in init_gl after GLUT context.
                renderer.mesh = load_legacy_mesh(obj_path, upload=False)
                print(f"✅ Loaded teapot from {obj_path}")
            except Exception as exc:
                print(f"❌ Error loading teapot data: {exc}")
                print("   Using fallback wireframe teapot instead.")

        renderer.run()
    except Exception as exc:
        print(f"❌ Error running legacy teapot renderer: {exc}")
        print("   This might be due to OpenGL context issues.")
        print("   On Linux/Wayland, try: PYOPENGL_PLATFORM=glx python ...")
        print("   Try running with different OpenGL settings or drivers.")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
