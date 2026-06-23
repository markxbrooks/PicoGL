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

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from examples.glut_renderer import GlutRenderer, set_up_legacy_lighting
from picogl.backend.gl.capability import GLMaterialFace, GLFixedFunctionCapability, GLPipelineCapability
from picogl.backend.gl.enums import GLDrawMode, GLBitMask
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.state.fill import GLCapability, GLColorMaterialMode, GLFillMode
from picogl.backend.gl.state.immediate import immediate_drawing
from picogl.backend.gl.wrappers.clear import gl_clear, gl_clear_color
from picogl.backend.gl.wrappers.enable import gl_enable, gl_disable
from picogl.backend.gl.wrappers.polygon_mode import gl_polygon_mode


class SimpleTeapotRenderer(GlutRenderer):
    """Simple teapot renderer using only built-in OpenGL primitives."""

    def __init__(self, width=800, height=600, title="Simple Legacy Teapot"):
        super().__init__(width, height, title)
        self.width = width
        self.height = height
        self.title = title
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.zoom_distance = 5.0
        self.wireframe_mode = False
        self.show_normals = False

    def init_glut(self):
        """Initialize GLUT window."""
        self.initialize_glut()
        glutIdleFunc(self.idle)

    def init_gl(self):
        """Initialize OpenGL state."""
        try:
            dark_blue_background = (0.1, 0.1, 0.2, 1.0)
            gl_clear_color(dark_blue_background)  # Dark blue background
            gl_enable(GLPipelineCapability.DEPTH_TEST)
            gl_enable(GLFixedFunctionCapability.LIGHTING)
            gl_enable(GLFixedFunctionCapability.LIGHT0)
            gl_enable(GLCapability.COLOR_MATERIAL)
            glColorMaterial(GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE)

            set_up_legacy_lighting()

        except Exception as e:
            print(f"Warning: OpenGL initialization issue: {e}")
            print("Continuing with basic rendering...")

    def display(self):
        """Display callback - render the scene."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        glLoadIdentity()

        # Set up camera
        gluLookAt(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

        # Draw the teapot
        self.draw_teapot()

        glutSwapBuffers()

    def draw_teapot(self):
        """Draw the teapot using built-in OpenGL primitives."""
        # Set polygon mode
        if self.wireframe_mode:
            gl_polygon_mode(GL_FRONT_AND_BACK, GL_LINE)
            gl_disable(GLFixedFunctionCapability.LIGHTING)
            glColor3f(1.0, 0.0, 0.0)  # Red wireframe
        else:
            gl_polygon_mode(GL_FRONT_AND_BACK, GL_FILL)
            gl_enable(GLFixedFunctionCapability.LIGHTING)
            glColor3f(0.8, 0.2, 0.2)  # Red teapot

        # Draw the teapot
        glutSolidTeapot(1.0)

        # Draw normals if enabled
        if self.show_normals and not self.wireframe_mode:
            self.draw_normals()

        # Reset polygon mode
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    def draw_normals(self):
        """Draw normal vectors (simplified)."""
        gl_disable(GLFixedFunctionCapability.LIGHTING)
        glColor3f(0.0, 1.0, 0.0)  # Green normals
        with immediate_drawing(GLDrawMode.LINES):
            # Draw a few normal vectors for demonstration
            for i in range(0, 360, 30):
                angle = i * 3.14159 / 180.0
                x = 0.5 * np.cos(angle)
                y = 0.5 * np.sin(angle)
                z = 0.0

                # Normal vector (simplified)
                nx = x
                ny = y
                nz = z

                glVertex3f(x, y, z)
                glVertex3f(x + nx * 0.2, y + ny * 0.2, z + nz * 0.2)

        gl_enable(GL_LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GLLegacyMatrixMode.PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GLLegacyMatrixMode.MODELVIEW)

    def keyboard(self, key, x, y):
        """Keyboard callback."""
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.rotation_x = 0.0
            self.rotation_y = 0.0
        elif key == b"w":  # Toggle wireframe mode
            self.wireframe_mode = not self.wireframe_mode
        elif key == b"n":  # Toggle normals
            self.show_normals = not self.show_normals
        elif key == b"f":  # Fill mode
            self.wireframe_mode = False
        elif key == b"+":  # Zoom in
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif key == b"-":  # Zoom out
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        elif key == b" ":  # Space bar - auto rotate
            self.auto_rotate = not getattr(self, "auto_rotate", False)

        glutPostRedisplay()

    def idle(self):
        """Idle callback for animation."""
        if getattr(self, "auto_rotate", False):
            self.rotation_y += 0.5
            glutPostRedisplay()

    def run(self):
        """Run the application."""
        self.init_glut()
        self.init_gl()

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Toggle wireframe mode")
        print("   F: Fill mode")
        print("   N: Toggle normals display")
        print("   +/-: Zoom in/out")
        print("   Space: Toggle auto-rotation")
        print("   ESC: Exit")
        print("\n🚀 Starting simple legacy teapot renderer...")

        glutMainLoop()


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
