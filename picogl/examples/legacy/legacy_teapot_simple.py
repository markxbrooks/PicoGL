"""Simple Legacy PicoGL Teapot - No external files required.

This is the simplest possible teapot renderer that works on any system
with basic OpenGL support, including older macOS systems.

Features:
- Uses only built-in OpenGL primitives (glutSolidTeapot)
- No external OBJ files required
- No modern shaders required
- Works with OpenGL 1.x/2.x
- Interactive rotation and zoom
"""
from picogl.backend.glut.buffers import glut_swap_buffers
from picogl.backend.glut.display import glut_post_redisplay
from picogl.backend.glut.glut_renderer import GlutRenderer
from picogl.backend.glut.idle import glut_idle_func
from picogl.core.draw.teapot import draw_teapot_with_normals
from picoui.dimensions import Dimensions


class SimpleTeapotRenderer(GlutRenderer):
    """Simple teapot renderer using only built-in OpenGL primitives."""

    def __init__(self, width=800, height=600, title="Simple Legacy Teapot"):
        self.dimensions = Dimensions(width=800, height=600)
        super().__init__(self.dimensions.width, self.dimensions.height, title)
        self.width = width
        self.height = height
        self.title = title
        self.zoom_distance = 5.0
        self.wireframe_mode = False
        self.show_normals = False

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glut_idle_func(self.idle)

    def draw_mesh(self):
        # Draw the teapot
        draw_teapot_with_normals(self.wireframe_mode, self.show_normals)

        glut_swap_buffers()

    def idle(self):
        """Idle callback for animation."""
        if getattr(self, "auto_rotate", False):
            self.rotation.y += 0.5
            glut_post_redisplay()


def main():
    """Main function."""
    try:
        # Check if we're in a headless environment
        import os

        if os.environ.get("DISPLAY") is None and os.name != "nt":
            print("❌ No display available. This requires a graphical environment.")
            print("   Try running on a system with X11, Wayland, or macOS display.")
            return

        renderer = SimpleTeapotRenderer(
            width=800,
            height=600,
            title="Simple Legacy PicoGL Teapot (OpenGL 1.x Compatible)",
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running simple teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
