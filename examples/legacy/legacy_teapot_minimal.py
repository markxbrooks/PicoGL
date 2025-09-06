#!/usr/bin/env python3
"""Minimal Legacy PicoGL Teapot - Maximum Compatibility.

This is the most basic teapot renderer possible that works on any system
with basic OpenGL support, including older macOS systems.

Features:
- Uses only built-in OpenGL primitives
- No external dependencies beyond PyOpenGL
- No PicoGL library required
- Works with OpenGL 1.x/2.x
- Interactive rotation and zoom
- Minimal error handling for maximum compatibility
"""

import sys
import os

# Check for display before importing OpenGL
if os.environ.get('DISPLAY') is None and os.name != 'nt':
    print("❌ No display available. This requires a graphical environment.")
    print("   Try running on a system with X11, Wayland, or macOS display.")
    sys.exit(1)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except ImportError as e:
    print(f"❌ Failed to import OpenGL modules: {e}")
    print("   Install with: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)


class MinimalTeapotRenderer:
    """Minimal teapot renderer using only built-in OpenGL primitives."""
    
    def __init__(self, width=800, height=600, title="Minimal Legacy Teapot"):
        self.width = width
        self.height = height
        self.title = title
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.zoom_distance = 5.0
        self.wireframe_mode = False
        
    def init_glut(self):
        """Initialize GLUT window."""
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title.encode('utf-8'))
        
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
        self.draw_teapot()
        
        glutSwapBuffers()
    
    def draw_teapot(self):
        """Draw the teapot using built-in OpenGL primitives."""
        # Set polygon mode
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 0.0, 0.0)  # Red wireframe
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glEnable(GL_LIGHTING)
            glColor3f(0.8, 0.2, 0.2)  # Red teapot
        
        # Draw the teapot
        glutSolidTeapot(1.0)
        
        # Reset polygon mode
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
        if key == b'\x1b':  # ESC key
            sys.exit(0)
        elif key == b'r':  # Reset rotation
            self.rotation_x = 0.0
            self.rotation_y = 0.0
        elif key == b'w':  # Toggle wireframe mode
            self.wireframe_mode = not self.wireframe_mode
        elif key == b'f':  # Fill mode
            self.wireframe_mode = False
        elif key == b'+':  # Zoom in
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif key == b'-':  # Zoom out
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        
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
        
        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   Mouse wheel: Zoom in/out")
        print("   R: Reset rotation")
        print("   W: Toggle wireframe mode")
        print("   F: Fill mode")
        print("   +/-: Zoom in/out")
        print("   ESC: Exit")
        print("\n🚀 Starting minimal legacy teapot renderer...")
        
        glutMainLoop()


def main():
    """Main function."""
    print("🧪 Minimal Legacy PicoGL Teapot")
    print("=" * 40)
    
    try:
        renderer = MinimalTeapotRenderer(
            width=800,
            height=600,
            title="Minimal Legacy PicoGL Teapot (OpenGL 1.x Compatible)"
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running minimal teapot renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
