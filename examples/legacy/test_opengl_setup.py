#!/usr/bin/env python3
"""Test OpenGL setup for PicoGL legacy teapot examples.

This script tests OpenGL capabilities without requiring a display,
helping diagnose issues with the legacy teapot renderers.
"""

import sys
import os

def test_opengl_imports():
    """Test if OpenGL modules can be imported."""
    print("Testing OpenGL imports...")
    
    try:
        import OpenGL.GL as GL
        print("  ✅ OpenGL.gl imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import OpenGL.gl: {e}")
        return False
    
    try:
        import OpenGL.GLU as GLU
        print("  ✅ OpenGL.GLU imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import OpenGL.GLU: {e}")
        return False
    
    try:
        import OpenGL.GLUT as GLUT
        print("  ✅ OpenGL.GLUT imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import OpenGL.GLUT: {e}")
        return False
    
    return True


def test_opengl_context():
    """Test if OpenGL context can be created."""
    print("\nTesting OpenGL context creation...")
    
    try:
        import OpenGL.GL as GL
        import OpenGL.GLUT as GLUT
        
        # Initialize GLUT
        GLUT.glutInit(sys.argv)
        GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
        GLUT.glutInitWindowSize(100, 100)
        
        # Create a small window
        window = GLUT.glutCreateWindow(b"Test Window")
        print("  ✅ GLUT window created successfully")
        
        # Test basic OpenGL functions
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        print("  ✅ Basic OpenGL functions work")
        
        # Test OpenGL version
        try:
            version = GL.glGetString(GL.GL_VERSION)
            if version:
                print(f"  ✅ OpenGL version: {version.decode()}")
            else:
                print("  ⚠️  OpenGL version not available")
        except:
            print("  ⚠️  Could not get OpenGL version")
        
        # Test OpenGL extensions
        try:
            extensions = GL.glGetString(GL.GL_EXTENSIONS)
            if extensions:
                ext_list = extensions.decode().split()
                print(f"  ✅ OpenGL extensions available: {len(ext_list)}")
                
                # Check for important extensions
                important_exts = ['GL_ARB_vertex_buffer_object', 'GL_ARB_vertex_array_object']
                for ext in important_exts:
                    if ext in ext_list:
                        print(f"    ✅ {ext}")
                    else:
                        print(f"    ⚠️  {ext} not available")
            else:
                print("  ⚠️  OpenGL extensions not available")
        except:
            print("  ⚠️  Could not get OpenGL extensions")
        
        # Clean up
        GLUT.glutDestroyWindow(window)
        print("  ✅ OpenGL context test completed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ OpenGL context creation failed: {e}")
        return False

def test_display_environment():
    """Test display environment."""
    print("\nTesting display environment...")
    
    # Check for display
    display = os.environ.get('DISPLAY')
    if display:
        print(f"  ✅ DISPLAY environment variable: {display}")
    else:
        print("  ⚠️  DISPLAY environment variable not set")
    
    # Check platform
    import platform
    system = platform.system()
    print(f"  ✅ Platform: {system}")
    
    if system == "Darwin":  # macOS
        print("  ℹ️  macOS detected - try running from Terminal.app or iTerm2")
    elif system == "Linux":
        print("  ℹ️  Linux detected - ensure X11 or Wayland is running")
    elif system == "Windows":
        print("  ℹ️  Windows detected - should work with standard OpenGL drivers")
    
    return True

def test_picogl_imports():
    """Test if PicoGL modules can be imported."""
    print("\nTesting PicoGL imports...")
    
    try:
        from picogl.renderer import MeshData
        print("  ✅ picogl.renderer.MeshData imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import picogl.renderer.MeshData: {e}")
        return False
    
    try:
        from picogl.renderer.legacy_glmesh import LegacyGLMesh
        print("  ✅ picogl.renderer.legacy_glmesh.LegacyGLMesh imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import LegacyGLMesh: {e}")
        return False
    
    try:
        from picogl.utils.loader.object import ObjectLoader
        print("  ✅ picogl.utils.loader.object.ObjectLoader imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import ObjectLoader: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 PicoGL Legacy Teapot - OpenGL Setup Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test OpenGL imports
    if not test_opengl_imports():
        all_tests_passed = False
    
    # Test display environment
    if not test_display_environment():
        all_tests_passed = False
    
    # Test PicoGL imports
    if not test_picogl_imports():
        all_tests_passed = False
    
    # Test OpenGL context (only if we have a display)
    if os.environ.get('DISPLAY') or os.name == 'nt':
        if not test_opengl_context():
            all_tests_passed = False
    else:
        print("\n⚠️  Skipping OpenGL context test (no display available)")
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All tests passed! Legacy teapot should work.")
        print("\n🚀 Try running:")
        print("   python legacy_teapot_simple.py")
        print("   python legacy_teapot_fixed.py")
    else:
        print("❌ Some tests failed. Check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install required packages: pip install PyOpenGL PyOpenGL_accelerate numpy")
        print("   2. On macOS: Run from Terminal.app or iTerm2")
        print("   3. On Linux: Ensure X11 or Wayland is running")
        print("   4. On Windows: Update graphics drivers")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
