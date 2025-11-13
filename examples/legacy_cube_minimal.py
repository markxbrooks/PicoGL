#!/usr/bin/env python3
"""Minimal Legacy PicoGL Cube - Maximum Compatibility.

This is the most basic cube renderer possible that works on any system
with basic OpenGL support, including older macOS systems.

Features:
- Uses only built-in OpenGL primitives
- No external dependencies beyond PyOpenGL
- No PicoGL library required
- Works with OpenGL 1.x/2.x
- Interactive rotation and zoom
- Colored cube with the same data as the original
"""

import sys
import os
import numpy as np

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


class MinimalCubeRenderer:
    """Minimal cube renderer using only built-in OpenGL primitives."""
    
    def __init__(self, width=800, height=600, title="Minimal Legacy Cube"):
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
        self.auto_rotate = False
        
        # Cube data (from cube_data.py)
        self.vertices = np.array([
            -1.0, -1.0, -1.0,  # 0
            -1.0, -1.0,  1.0,  # 1
            -1.0,  1.0,  1.0,  # 2
             1.0,  1.0, -1.0,  # 3
            -1.0, -1.0, -1.0,  # 4
            -1.0,  1.0, -1.0,  # 5
             1.0, -1.0,  1.0,  # 6
            -1.0, -1.0, -1.0,  # 7
             1.0, -1.0, -1.0,  # 8
             1.0,  1.0, -1.0,  # 9
             1.0, -1.0, -1.0,  # 10
            -1.0, -1.0, -1.0,  # 11
            -1.0, -1.0, -1.0,  # 12
            -1.0,  1.0,  1.0,  # 13
            -1.0,  1.0, -1.0,  # 14
             1.0, -1.0,  1.0,  # 15
            -1.0, -1.0,  1.0,  # 16
            -1.0, -1.0, -1.0,  # 17
            -1.0,  1.0,  1.0,  # 18
            -1.0, -1.0,  1.0,  # 19
             1.0, -1.0,  1.0,  # 20
             1.0,  1.0,  1.0,  # 21
             1.0, -1.0, -1.0,  # 22
             1.0,  1.0, -1.0,  # 23
             1.0, -1.0, -1.0,  # 24
             1.0,  1.0,  1.0,  # 25
             1.0, -1.0,  1.0,  # 26
             1.0,  1.0,  1.0,  # 27
             1.0,  1.0, -1.0,  # 28
            -1.0,  1.0, -1.0,  # 29
             1.0,  1.0,  1.0,  # 30
            -1.0,  1.0, -1.0,  # 31
            -1.0,  1.0,  1.0,  # 32
             1.0,  1.0,  1.0,  # 33
            -1.0,  1.0,  1.0,  # 34
             1.0, -1.0,  1.0   # 35
        ], dtype=np.float32)
        
        self.colors = np.array([
            0.583,  0.771,  0.014,  # 0
            0.609,  0.115,  0.436,  # 1
            0.327,  0.483,  0.844,  # 2
            0.822,  0.569,  0.201,  # 3
            0.435,  0.602,  0.223,  # 4
            0.310,  0.747,  0.185,  # 5
            0.597,  0.770,  0.761,  # 6
            0.559,  0.436,  0.730,  # 7
            0.359,  0.583,  0.152,  # 8
            0.483,  0.596,  0.789,  # 9
            0.559,  0.861,  0.639,  # 10
            0.195,  0.548,  0.859,  # 11
            0.014,  0.184,  0.576,  # 12
            0.771,  0.328,  0.970,  # 13
            0.406,  0.615,  0.116,  # 14
            0.676,  0.977,  0.133,  # 15
            0.971,  0.572,  0.833,  # 16
            0.140,  0.616,  0.489,  # 17
            0.997,  0.513,  0.064,  # 18
            0.945,  0.719,  0.592,  # 19
            0.543,  0.021,  0.978,  # 20
            0.279,  0.317,  0.505,  # 21
            0.167,  0.620,  0.077,  # 22
            0.347,  0.857,  0.137,  # 23
            0.055,  0.953,  0.042,  # 24
            0.714,  0.505,  0.345,  # 25
            0.783,  0.290,  0.734,  # 26
            0.722,  0.645,  0.174,  # 27
            0.302,  0.455,  0.848,  # 28
            0.225,  0.587,  0.040,  # 29
            0.517,  0.713,  0.338,  # 30
            0.053,  0.959,  0.120,  # 31
            0.393,  0.621,  0.362,  # 32
            0.673,  0.211,  0.457,  # 33
            0.820,  0.883,  0.371,  # 34
            0.982,  0.099,  0.879   # 35
        ], dtype=np.float32)
        
        # Reshape for easier access
        self.vertices = self.vertices.reshape(-1, 3)
        self.colors = self.colors.reshape(-1, 3)
        
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
        glutIdleFunc(self.idle)
        
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
        
        # Draw the cube
        self.draw_cube()
        
        glutSwapBuffers()
    
    def draw_cube(self):
        """Draw the cube using immediate mode OpenGL."""
        if self.wireframe_mode:
            glDisable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glColor3f(1.0, 0.0, 0.0)  # Red wireframe
        else:
            glEnable(GL_LIGHTING)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Draw the cube using immediate mode
        glBegin(GL_TRIANGLES)
        for i in range(0, len(self.vertices), 3):
            # Each triangle has 3 vertices
            for j in range(3):
                vertex_idx = i + j
                if vertex_idx < len(self.vertices):
                    # Set colour for this vertex
                    if not self.wireframe_mode:
                        glColor3f(
                            self.colors[vertex_idx][0],
                            self.colors[vertex_idx][1],
                            self.colors[vertex_idx][2]
                        )
                    
                    # Set vertex position
                    glVertex3f(
                        self.vertices[vertex_idx][0],
                        self.vertices[vertex_idx][1],
                        self.vertices[vertex_idx][2]
                    )
        glEnd()
        
        # Draw normals if enabled
        if self.show_normals and not self.wireframe_mode:
            self.draw_normals()
        
        # Reset polygon mode
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)
    
    def draw_normals(self):
        """Draw normal vectors (simplified)."""
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 1.0, 0.0)  # Green normals
        glBegin(GL_LINES)
        
        # Draw a few normal vectors for demonstration
        for i in range(0, len(self.vertices), 6):  # Every 6 vertices (2 triangles)
            if i + 2 < len(self.vertices):
                # Calculate normal for this triangle
                v1 = self.vertices[i]
                v2 = self.vertices[i + 1]
                v3 = self.vertices[i + 2]
                
                # Calculate two edge vectors
                edge1 = v2 - v1
                edge2 = v3 - v1
                
                # Calculate normal (cross product)
                normal = np.cross(edge1, edge2)
                normal = normal / np.linalg.norm(normal)  # Normalize
                
                # Center of triangle
                center = (v1 + v2 + v3) / 3.0
                
                # Draw normal vector
                glVertex3f(center[0], center[1], center[2])
                glVertex3f(
                    center[0] + normal[0] * 0.5,
                    center[1] + normal[1] * 0.5,
                    center[2] + normal[2] * 0.5
                )
        
        glEnd()
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
        elif key == b'n':  # Toggle normals
            self.show_normals = not self.show_normals
        elif key == b'f':  # Fill mode
            self.wireframe_mode = False
        elif key == b'+':  # Zoom in
            self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
        elif key == b'-':  # Zoom out
            self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
        elif key == b' ':  # Space bar - auto rotate
            self.auto_rotate = not self.auto_rotate
        
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
    
    def idle(self):
        """Idle callback for animation."""
        if self.auto_rotate:
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
        print("\n🚀 Starting minimal legacy cube renderer...")
        print(f"   Rendering {len(self.vertices)} vertices with {len(self.colors)} colors")
        
        glutMainLoop()


def main():
    """Main function."""
    print("🧪 Minimal Legacy PicoGL Cube")
    print("=" * 40)
    
    try:
        renderer = MinimalCubeRenderer(
            width=800,
            height=600,
            title="Minimal Legacy PicoGL Cube (OpenGL 1.x Compatible)"
        )
        renderer.run()
    except Exception as e:
        print(f"❌ Error running minimal cube renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")


if __name__ == "__main__":
    main()
