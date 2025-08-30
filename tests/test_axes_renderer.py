#!/usr/bin/env python3
"""
Test script for the AxesRenderer class.
This script tests the basic functionality of the axes renderer.
"""

import numpy as np
from OpenGL import GL
from OpenGL.GLUT import glutInit, glutCreateWindow, glutDisplayFunc, glutMainLoop
from OpenGL.GLU import gluPerspective

from picogl.backend.legacy.gizmos.axes.renderer import AxesRenderer

def init_gl():
    """Initialize OpenGL settings."""
    GL.glClearColor(0.0, 0.0, 0.0, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

def display():
    """Display function for GLUT."""
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    
    # Set up projection matrix
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 1000.0)
    
    # Set up modelview matrix
    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    GL.glTranslatef(0.0, 0.0, -100.0)
    GL.glRotatef(30, 1.0, 0.0, 0.0)
    GL.glRotatef(45, 0.0, 1.0, 0.0)
    
    # Render the axes
    try:
        axes_renderer.render_array()
        print("✅ Axes rendered successfully")
    except Exception as e:
        print(f"❌ Error rendering axes: {e}")
    
    GL.glFlush()

def main():
    """Main function."""
    global axes_renderer
    
    # Initialize GLUT
    glutInit()
    glutCreateWindow(b"Test Axes Renderer")
    
    # Initialize OpenGL
    init_gl()
    
    # Create and set up the axes renderer
    axes_renderer = AxesRenderer()
    
    # Set up a simple unit cell
    unit_cell_info = {
        'a': 50.0,
        'b': 50.0, 
        'c': 50.0,
        'alpha': 90.0,
        'beta': 90.0,
        'gamma': 90.0
    }
    
    # Initialize the axes
    axes_renderer.set_unit_cell(unit_cell_info)
    
    # Test the renderer
    print("Testing axes renderer...")
    print(f"Status: {axes_renderer.get_status()}")
    
    if axes_renderer.test_render():
        print("✅ Renderer test passed")
    else:
        print("❌ Renderer test failed")
    
    # Set display function and start main loop
    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == "__main__":
    main()
