"""Legacy PicoGL Teapot - Compatible with systems without modern shader support.

This example uses legacy OpenGL rendering (OpenGL 1.x/2.x) that works on:
- Older macOS systems
- Systems without modern OpenGL 3.3+ support
- Systems with limited shader support

The renderer uses LegacyGLMesh which bypasses modern VAO/VBO requirements
and uses legacy client states and immediate mode rendering.
"""

from pathlib import Path
from typing import Optional

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from picogl.renderer import MeshData
from picogl.renderer.legacy_glmesh import LegacyGLMesh
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
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.zoom_distance = 5.0
        self.object_file_name = object_file_name

    def init_glut(self):
        """Initialize GLUT window."""
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title.encode("utf-8"))

        # Set callbacks
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)

    def init_gl(self):
        """Initialize OpenGL state."""
        glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark blue background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

        # Set up material properties
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

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
                colors=mesh_data.colors.reshape(-1, 3)
                if mesh_data.colors is not None
                else None,
                normals=mesh_data.normals.reshape(-1, 3)
                if mesh_data.normals is not None
                else None,
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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up camera
        gluLookAt(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)

        # Apply rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

        # Draw the teapot
        if self.mesh:
            try:
                self.mesh.draw()
            except Exception as e:
                print(f"Error drawing mesh: {e}")
                # Fallback: draw a simple wireframe teapot
                self.draw_fallback_teapot()
        else:
            # Fallback: draw a simple wireframe teapot
            self.draw_fallback_teapot()

        glutSwapBuffers()

    def draw_fallback_teapot(self):
        """Draw a simple wireframe teapot as fallback."""
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.0, 0.0)  # Red wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glutWireTeapot(1.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)

    def reshape(self, width, height):
        """Reshape callback - handle window resize."""
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def keyboard(self, key, x, y):
        """Keyboard callback."""
        if key == b"\x1b":  # ESC key
            sys.exit(0)
        elif key == b"r":  # Reset rotation
            self.rotation_x = 0.0
            self.rotation_y = 0.0
        elif key == b"w":  # Wireframe mode
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        elif key == b"f":  # Fill mode
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        """Mouse callback."""
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.last_mouse_x = x
                self.last_mouse_y = y
            else:
                self.last_mouse_x = None
                self.last_mouse_y = None
        elif button == 3:  # Mouse wheel up
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif button == 4:  # Mouse wheel down
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        glutPostRedisplay()

    def motion(self, x, y):
        """Mouse motion callback."""
        if self.last_mouse_x is not None and self.last_mouse_y is not None:
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            # Clamp rotation
            self.rotation_x = max(-90, min(90, self.rotation_x))

            self.last_mouse_x = x
            self.last_mouse_y = y
            glutPostRedisplay()

    def run(self):
        """Run the application."""
        self.init_glut()
        self.init_gl()

        if not self.object_file_name.exists():
            print(f"❌ Teapot OBJ file not found at {obj_file_path}")
            print("   Using fallback wireframe teapot instead.")
        else:
            if not self.load_object_data(str(self.object_file_name)):
                print("   Using fallback wireframe teapot instead.")

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Wireframe mode")
        print("   F: Fill mode")
        print("   ESC: Exit")
        print("\n🚀 Starting legacy teapot renderer...")

        glutMainLoop()


def main():
    """Main function."""
    try:
        # Load teapot data
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
