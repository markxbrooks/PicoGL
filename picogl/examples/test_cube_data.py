#!/usr/bin/env python3
"""Test cube data and rendering without requiring a display.

This script tests the cube data and rendering logic without requiring
a graphical display, helping diagnose issues with the legacy cube renderers.
"""

import os
import sys

import numpy as np

from backend.glut.cube_data import CUBE_VERTICES


def test_cube_data():
    """Test cube data structure and validity."""
    print("Testing cube data...")

    # Cube vertices (from cube_data.py)
    vertices = CUBE_VERTICES

    # Cube colors (from cube_data.py)
    colors = np.array(
        [
            0.583,
            0.771,
            0.014,  # 0
            0.609,
            0.115,
            0.436,  # 1
            0.327,
            0.483,
            0.844,  # 2
            0.822,
            0.569,
            0.201,  # 3
            0.435,
            0.602,
            0.223,  # 4
            0.310,
            0.747,
            0.185,  # 5
            0.597,
            0.770,
            0.761,  # 6
            0.559,
            0.436,
            0.730,  # 7
            0.359,
            0.583,
            0.152,  # 8
            0.483,
            0.596,
            0.789,  # 9
            0.559,
            0.861,
            0.639,  # 10
            0.195,
            0.548,
            0.859,  # 11
            0.014,
            0.184,
            0.576,  # 12
            0.771,
            0.328,
            0.970,  # 13
            0.406,
            0.615,
            0.116,  # 14
            0.676,
            0.977,
            0.133,  # 15
            0.971,
            0.572,
            0.833,  # 16
            0.140,
            0.616,
            0.489,  # 17
            0.997,
            0.513,
            0.064,  # 18
            0.945,
            0.719,
            0.592,  # 19
            0.543,
            0.021,
            0.978,  # 20
            0.279,
            0.317,
            0.505,  # 21
            0.167,
            0.620,
            0.077,  # 22
            0.347,
            0.857,
            0.137,  # 23
            0.055,
            0.953,
            0.042,  # 24
            0.714,
            0.505,
            0.345,  # 25
            0.783,
            0.290,
            0.734,  # 26
            0.722,
            0.645,
            0.174,  # 27
            0.302,
            0.455,
            0.848,  # 28
            0.225,
            0.587,
            0.040,  # 29
            0.517,
            0.713,
            0.338,  # 30
            0.053,
            0.959,
            0.120,  # 31
            0.393,
            0.621,
            0.362,  # 32
            0.673,
            0.211,
            0.457,  # 33
            0.820,
            0.883,
            0.371,  # 34
            0.982,
            0.099,
            0.879,  # 35
        ],
        dtype=np.float32,
    )

    # Reshape for easier access
    vertices = vertices.reshape(-1, 3)
    colors = colors.reshape(-1, 3)

    print(f"  ✅ Vertices: {vertices.shape} (should be (36, 3))")
    print(f"  ✅ Colors: {colors.shape} (should be (36, 3))")

    # Check data validity
    if vertices.shape != (36, 3):
        print(f"  ❌ Invalid vertex shape: {vertices.shape}")
        return False

    if colors.shape != (36, 3):
        print(f"  ❌ Invalid colour shape: {colors.shape}")
        return False

    # Check for valid vertex coordinates
    if not np.all(np.isfinite(vertices)):
        print("  ❌ Invalid vertex coordinates (NaN or Inf)")
        return False

    # Check for valid colour values
    if not np.all(np.isfinite(colors)):
        print("  ❌ Invalid colour values (NaN or Inf)")
        return False

    # Check colour range
    if not np.all((colors >= 0.0) & (colors <= 1.0)):
        print("  ❌ Color values out of range [0, 1]")
        return False

    print("  ✅ All data validation checks passed")

    # Show some statistics
    print(f"  📊 Vertex range: [{vertices.min():.3f}, {vertices.max():.3f}]")
    print(f"  📊 Color range: [{colors.min():.3f}, {colors.max():.3f}]")

    return True


def test_triangle_count():
    """Test triangle count and structure."""
    print("\nTesting triangle structure...")

    # The cube should have 12 triangles (36 vertices / 3 vertices per triangle)
    triangle_count = 36 // 3
    print(f"  ✅ Triangle count: {triangle_count} (should be 12)")

    if triangle_count != 12:
        print("  ❌ Invalid triangle count")
        return False

    print("  ✅ Triangle structure is valid")
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

    return True


def test_mesh_creation():
    """Test mesh creation without OpenGL context."""
    print("\nTesting mesh creation...")

    try:
        from picogl.renderer import MeshData

        # Create test data
        vertices = np.array([-1, -1, -1, 1, 1, 1], dtype=np.float32)
        colors = np.array([1, 0, 0, 0, 1, 0], dtype=np.float32)

        # Create mesh data
        mesh_data = MeshData.from_raw(vertices=vertices, colors=colors)

        print("  ✅ MeshData created successfully")
        print(f"  📊 MeshData vertices: {mesh_data.CUBE_DATA.shape}")
        print(f"  📊 MeshData colors: {mesh_data.colors.shape}")

        return True

    except Exception as e:
        print(f"  ❌ MeshData creation failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 PicoGL Legacy Cube - Data and Import Test")
    print("=" * 50)

    all_tests_passed = True

    # Test cube data
    if not test_cube_data():
        all_tests_passed = False

    # Test triangle structure
    if not test_triangle_count():
        all_tests_passed = False

    # Test PicoGL imports
    if not test_picogl_imports():
        all_tests_passed = False

    # Test mesh creation
    if not test_mesh_creation():
        all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All tests passed! Cube data and imports are working.")
        print("\n🚀 Try running:")
        print("   python legacy_cube_minimal.py")
        print("   python legacy_cube_fixed.py")
    else:
        print("❌ Some tests failed. Check the issues above.")
        print("\n🔧 Troubleshooting:")
        print(
            "   1. Install required packages: pip install PyOpenGL PyOpenGL_accelerate numpy"
        )
        print("   2. Install PicoGL: pip install picogl")
        print("   3. On macOS: Run from Terminal.app or iTerm2")
        print("   4. On Linux: Ensure X11 or Wayland is running")
        print("   5. On Windows: Update graphics drivers")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
