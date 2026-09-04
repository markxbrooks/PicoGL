"""
Qt-based Cube Renderer using PicoGL's GLBase

This example demonstrates how to create a simple cube renderer using Qt's QOpenGLWidget
through PicoGL's GLBase class. It's designed for legacy displays and systems that
prefer Qt over GLUT.

Features:
- Legacy OpenGL rendering (compatible with older systems)
- Mouse controls for rotation and zoom
- Colorful cube with vertex colors
- Qt-based window management
- Cross-platform compatibility

Requirements:
- PySide6 (Qt6)
- PyOpenGL
- NumPy
- PicoGL

Usage:
    python examples/legacy_qt_cube.py
"""

import sys

from PySide6.QtWidgets import QApplication

from picogl.examples.legacy_qt_cube_simple import SimpleQtCubeWidget

# OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError as e:
    print("❌ Error: PyOpenGL not available")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)


def main():
    """Main function to run the Qt cube renderer"""
    print("🚀 Starting PicoGL Qt Cube Renderer...")

    # Check for Qt availability
    try:
        app = QApplication(sys.argv)
    except ImportError as e:
        print("❌ Error: PySide6 not available")
        print("Please install PySide6: pip install PySide6")
        return 1

    # Create and show window
    window = SimpleQtCubeWidget()
    window.show()

    print("✅ Qt Cube Renderer started successfully!")
    print("   - Window: 800x600")
    print("   - Rendering: Legacy OpenGL")
    print("   - Controls: Mouse drag, wheel, keyboard")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
