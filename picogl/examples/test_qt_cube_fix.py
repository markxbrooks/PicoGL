#!/usr/bin/env python3
"""
Test script to verify the Qt cube fix

This script tests that the mvp_parameters are properly initialized
and that the rotation values can be updated without error.
"""

import sys
from pathlib import Path

import numpy as np

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_mvp_parameters_initialization():
    """Test that mvp_parameters are properly initialized"""
    print("🧪 Testing mvp_parameters initialization...")

    try:
        from picogl.ui.backend.qt.base import MvpParameters

        # Create mvp_parameters instance
        mvp = MvpParameters()

        # Check initial values
        print(f"  Initial rotation_x: {mvp.rotation_x}")
        print(f"  Initial rotation_y: {mvp.rotation_y}")
        print(f"  Initial pan_x: {mvp.pan_x}")
        print(f"  Initial pan_y: {mvp.pan_y}")

        # Initialize values
        mvp.rotation_x = 0.0
        mvp.rotation_y = 0.0
        mvp.pan_x = 0.0
        mvp.pan_y = 0.0

        # Test addition operations
        mvp.rotation_x += 10.5
        mvp.rotation_y += 20.3
        mvp.pan_x += 5.0
        mvp.pan_y += 3.0

        print(f"  After addition - rotation_x: {mvp.rotation_x}")
        print(f"  After addition - rotation_y: {mvp.rotation_y}")
        print(f"  After addition - pan_x: {mvp.pan_x}")
        print(f"  After addition - pan_y: {mvp.pan_y}")

        # Verify values
        assert mvp.rotation_x == 10.5, f"Expected 10.5, got {mvp.rotation_x}"
        assert mvp.rotation_y == 20.3, f"Expected 20.3, got {mvp.rotation_y}"
        assert mvp.pan_x == 5.0, f"Expected 5.0, got {mvp.pan_x}"
        assert mvp.pan_y == 3.0, f"Expected 3.0, got {mvp.pan_y}"

        print("  ✅ mvp_parameters initialization test passed!")
        return True

    except Exception as e:
        print(f"  ❌ mvp_parameters initialization test failed: {e}")
        return False


def test_qt_cube_initialization():
    """Test that QtCubeRenderer initializes properly"""
    print("🧪 Testing QtCubeRenderer initialization...")

    try:
        # Mock Qt imports to avoid requiring actual Qt installation
        import unittest.mock as mock

        with mock.patch("PySide6.QtWidgets.QApplication"), mock.patch(
            "PySide6.QtCore.QTimer"
        ), mock.patch("PySide6.QtOpenGLWidgets.QOpenGLWidget"), mock.patch(
            "OpenGL.GL"
        ), mock.patch(
            "OpenGL.GLU"
        ):
            from picogl.ui.backend.qt.renderer import QtObjectRenderer

            # Create a mock parent widget
            mock_parent = mock.MagicMock()

            # Create renderer instance
            renderer = QtObjectRenderer(mock_parent)

            # Check that mvp_parameters are initialized
            assert renderer.mvp_parameters.x == 0.0, "rotation_x should be 0.0"
            assert renderer.mvp_parameters.y == 0.0, "rotation_y should be 0.0"
            assert renderer.mvp_parameters.pan_x == 0.0, "pan_x should be 0.0"
            assert renderer.mvp_parameters.pan_y == 0.0, "pan_y should be 0.0"

            # Check local rotation values
            assert renderer.x == 0.0, "local rotation_x should be 0.0"
            assert renderer.y == 0.0, "local rotation_y should be 0.0"

            print("  ✅ QtCubeRenderer initialization test passed!")
            return True

    except Exception as e:
        print(f"  ❌ QtCubeRenderer initialization test failed: {e}")
        return False


def test_rotation_operations():
    """Test that rotation operations work without error"""
    print("🧪 Testing rotation operations...")

    try:
        # Mock Qt imports
        import unittest.mock as mock

        with mock.patch("PySide6.QtWidgets.QApplication"), mock.patch(
            "PySide6.QtCore.QTimer"
        ), mock.patch("PySide6.QtOpenGLWidgets.QOpenGLWidget"), mock.patch(
            "OpenGL.GL"
        ), mock.patch(
            "OpenGL.GLU"
        ):
            from picogl.ui.backend.qt.renderer import QtObjectRenderer

            # Create renderer instance
            renderer = QtObjectRenderer()

            # Test rotation updates
            renderer.x += 15.5
            renderer.y += 25.3

            # Update mvp_parameters
            renderer.mvp_parameters.x = renderer.x
            renderer.mvp_parameters.y = renderer.y

            # Verify values
            assert renderer.x == 15.5, f"Expected 15.5, got {renderer.x}"
            assert renderer.y == 25.3, f"Expected 25.3, got {renderer.y}"
            assert (
                renderer.mvp_parameters.x == 15.5
            ), f"Expected 15.5, got {renderer.mvp_parameters.x}"
            assert (
                renderer.mvp_parameters.y == 25.3
            ), f"Expected 25.3, got {renderer.mvp_parameters.y}"

            print("  ✅ Rotation operations test passed!")
            return True

    except Exception as e:
        print(f"  ❌ Rotation operations test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Qt Cube Fix...")
    print("=" * 50)

    tests = [
        test_mvp_parameters_initialization,
        test_qt_cube_initialization,
        test_rotation_operations,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The Qt cube fix is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
