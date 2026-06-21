
import os
import sys
from math import cos, sin

import numpy as np
from picogl.state.draw_mode import GLDrawMode
from picogl.state.immediate import immediate_drawing
# Check for display before importing OpenGL
if os.environ.get("DISPLAY") is None and os.name != "nt":
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

# Optional: if you want to demonstrate templating
try:
    from jinja2 import Template
except ImportError:
    print("⚠️  Jinja2 not available, template functionality disabled")
    Template = None

# -------------------------------
# Quad data (two triangles) with normals
# -------------------------------
# Quad in the XY plane, at z = -5
# We'll define four corners and two triangles (0-1-2 and 2-3-0)
quad_verts = [
    {'pos': [-1.0,  1.0, -5.0], 'normal': [0.0, 0.0, 1.0] , 'colour': [1.0, 0.0, 1.0]},  # top-left
    {'pos': [ 1.0,  1.0, -5.0], 'normal': [0.0, 0.0, 1.0] , 'colour': [0.0, 1.0, 1.0]},  # top-right
    {'pos': [ 1.0, -1.0, -5.0], 'normal': [0.0, 0.0, 1.0] , 'colour': [0.0, 0.0, 1.0]},  # bottom-right
    {'pos': [-1.0, -1.0, -5.0], 'normal': [0.0, 0.0, 1.0] , 'colour': [0.0, 0.0, 1.0]},  # bottom-left
]

# Indices for two triangles
quad_indices = [
    (0, 1, 2),
    (2, 3, 0),
]

# Uniforms (we'll rotate model around Y and X with mouse)
model = np.identity(4, dtype=np.float32)
view  = np.identity(4, dtype=np.float32)
proj  = np.identity(4, dtype=np.float32)


# Camera-ish projection
def update_projection(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / float(height) if height > 0 else 1.0
    gluPerspective(45.0, aspect, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# -------------------------------
#  A tiny Jinja2 vertex shader
# -------------------------------
template_src = """def process_vertex(v, mvp_matrix):
    # Position processing
    pos = np.array(v['pos'] + [1.0])
    gl_pos = (mvp_matrix @ pos).tolist()

    # Color processing: {{ color_mode }}
{% if color_mode == "vertex_color" %}
    colour = v['colour']
{% elif color_mode == "normal_based" %}
    n = np.array(v['normal'], dtype=float)
    n_norm = n / np.linalg.norm(n) if np.linalg.norm(n) != 0 else n
    colour = [(n_norm[0]*0.5)+0.5, (n_norm[1]*0.5)+0.5, (n_norm[2]*0.5)+0.5]
{% elif color_mode == "custom" %}
    colour = {{ custom_color_expression }}
{% endif %}

    return {'gl_pos': gl_pos, 'colour': colour}"""
template = Template(template_src) if Template else None

def render_vertex_with_template(v, mvp):
    # This demonstrates where you could render a template per-vertex.
    # For now, we compute directly; the template is shown for educational purposes.
    # Build a 4D pos
    p = v['pos'] + [1.0]
    # MVP-like transform: p' = MVP * p
    # Compute using numpy for accuracy
    gl_pos = (mvp @ np.array(p, dtype=np.float32)).tolist()
    # Color from normal
    n = np.array(v['normal'], dtype=float)
    nm = np.linalg.norm(n)
    if nm != 0:
        n_norm = (n / nm).tolist()
    else:
        n_norm = n.tolist()
    color = v['colour']
    return {'gl_pos': gl_pos, 'colour': color}

# -------------------------------
# Interaction: mouse-driven rotation
# -------------------------------
rot_x, rot_y = 0.0, 0.0
dragging = False
last_x, last_y = 0, 0

def mouse(button, state, x, y):
    global dragging, last_x, last_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            dragging = True
            last_x, last_y = x, y
        else:
            dragging = False

def motion(x, y):
    global rot_x, rot_y, last_x, last_y
    if dragging:
        dx = x - last_x
        dy = y - last_y
        last_x, last_y = x, y
        # Update rotation angles (sensitivity)
        rot_y += dx * 0.5
        rot_x += dy * 0.5
        glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b':  # ESC
        sys.exit()

# -------------------------------
# Jinja2 vertex processor generation
# -------------------------------
def create_vertex_program(color_mode, custom_expr=None):
    if Template is None:
        # Fallback implementation when Jinja2 is not available
        """def process_vertex(v, mvp_matrix):
            # Position processing
            pos = np.array(v['pos'] + [1.0])
            gl_pos = (mvp_matrix @ pos).tolist()
            
            # Color processing based on mode
            if color_mode == "vertex_color":
                colour = v['colour']
            elif color_mode == "normal_based":
                n = np.array(v['normal'], dtype=float)
                n_norm = n / np.linalg.norm(n) if np.linalg.norm(n) != 0 else n
                colour = [(n_norm[0]*0.5)+0.5, (n_norm[1]*0.5)+0.5, (n_norm[2]*0.5)+0.5]
            elif color_mode == "custom" and custom_expr:
                colour = eval(custom_expr, {'v': v, 'np': np})
            else:
                colour = v['colour']  # Default to vertex colour
            
            return {'gl_pos': gl_pos, 'colour': colour}
        return process_vertex"""
    
    # Jinja2 template-based implementation
    template = Template(template_src)
    context = {'color_mode': color_mode}
    if custom_expr:
        context['custom_color_expression'] = custom_expr

    processor_code = template.render(**context)
    # Make sure numpy is available in the executed code
    exec_globals = {'np': np}
    exec(processor_code, exec_globals)
    return exec_globals['process_vertex']

# -------------------------------
# OpenGL setup and render loop
# -------------------------------
def init_gl():
    glClearColor(0.15, 0.15, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Simple camera: place back a bit and apply rotations
    glTranslatef(0.0, 0.0, -8.0)

    # Apply rotations from mouse
    glRotatef(rot_x, 1.0, 0.0, 0.0)
    glRotatef(rot_y, 0.0, 1.0, 0.0)

    # Create MVP matrix for the vertex processor
    # Since we're using fixed-function OpenGL, we'll create a simple identity matrix
    # In a real implementation, you'd build this from model, view, and projection matrices
    mvp_matrix = np.identity(4, dtype=np.float32)

    # Create vertex processor with vertex colors
    vertex_processor = create_vertex_program("vertex_color")

    render(mvp_matrix, vertex_processor)

    glutSwapBuffers()


def render(mvp_matrix, vertex_processor):
    with immediate_drawing(GLDrawMode.TRIANGLES):
        for idx in quad_indices:
            for i in idx:
                v = quad_verts[i]
                result = vertex_processor(v, mvp_matrix)
                glColor3f(*result['colour'])
                glVertex3f(*v['pos'])


def reshape(width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / float(height)
    gluPerspective(45.0, aspect, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    try:
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutCreateWindow(b"Quad with mouse rotation - PyOpenGL + GLUT (legacy gl)")

        init_gl()
        glutDisplayFunc(display)
        glutReshapeFunc(reshape)
        glutMouseFunc(mouse)
        glutMotionFunc(motion)
        glutKeyboardFunc(keyboard)

        print("\n🎮 Controls:")
        print("   Mouse: Rotate view")
        print("   ESC: Exit")
        print("\n🚀 Starting quad renderer...")


        # Initial projection setup (in reshape)
        glutMainLoop()
    except Exception as e:
        print(f"❌ Error running quad renderer: {e}")
        print("   This might be due to OpenGL context issues.")
        print("   Try running with different OpenGL settings or drivers.")
        print("   On macOS, try running from Terminal.app or iTerm2.")

if __name__ == "__main__":
    main()








