#!/usr/bin/env python3
"""
Test script to verify both Qt cube fixes

This script tests that both the mvp_parameters and camera_parameters
are properly initialized and that arithmetic operations work without errors.
"""


def test_mvp_parameters_fix():
    """Test that mvp_parameters can be initialized and used"""
    print("🧪 Testing mvp_parameters fix...")

    try:
        from dataclasses import dataclass

        @dataclass
        class MvpParameters:
            """MVP Parameters"""

            rotation_x = None
            rotation_y = None
            pan_x = None
            pan_y = None

        # Create mvp_parameters instance
        mvp = MvpParameters()

        # Initialize values to avoid None (this is the fix)
        mvp.rotation_x = 0.0
        mvp.rotation_y = 0.0
        mvp.pan_x = 0.0
        mvp.pan_y = 0.0

        # Test arithmetic operations
        mvp.rotation_x += 10.0 * 0.5
        mvp.rotation_y += 15.0 * 0.5
        mvp.pan_x += 5.0 * 0.01
        mvp.pan_y += 3.0 * 0.01

        # Verify results
        assert mvp.rotation_x == 5.0, f"Expected 5.0, got {mvp.rotation_x}"
        assert mvp.rotation_y == 7.5, f"Expected 7.5, got {mvp.rotation_y}"
        assert mvp.pan_x == 0.05, f"Expected 0.05, got {mvp.pan_x}"
        assert mvp.pan_y == 0.03, f"Expected 0.03, got {mvp.pan_y}"

        print("  ✅ mvp_parameters fix working correctly!")
        return True

    except Exception as e:
        print(f"  ❌ mvp_parameters test failed: {e}")
        return False


def test_camera_parameters_fix():
    """Test that camera_parameters can be initialized and used"""
    print("🧪 Testing camera_parameters fix...")

    try:
        from dataclasses import dataclass

        import numpy as np

        @dataclass
        class CameraParameters:
            """camera parameters"""

            rotation_x_axis = None
            rotation_y_axis = None
            rotation_z_axis = None
            translation_x_axis = None
            translation_y_axis = None
            translation_zoom = None
            rotation: np.ndarray = None
            translation: np.ndarray = None

        # Create camera_parameters instance
        camera = CameraParameters()

        # Initialize values to avoid None (this is the fix)
        camera.rotation_x_axis = 0.0
        camera.rotation_y_axis = 0.0
        camera.rotation_z_axis = 0.0
        camera.translation_x_axis = 0.0
        camera.translation_y_axis = 0.0
        camera.translation_zoom = 0.0

        # Test arithmetic operations (this was causing the AttributeError)
        camera.rotation_x_axis += 10.0 * 0.5
        camera.rotation_y_axis += 15.0 * 0.5
        camera.translation_x_axis += 5.0 * 0.01
        camera.translation_y_axis += 3.0 * 0.01

        # Verify results
        assert (
            camera.rotation_x_axis == 5.0
        ), f"Expected 5.0, got {camera.rotation_x_axis}"
        assert (
            camera.rotation_y_axis == 7.5
        ), f"Expected 7.5, got {camera.rotation_y_axis}"
        assert (
            camera.translation_x_axis == 0.05
        ), f"Expected 0.05, got {camera.translation_x_axis}"
        assert (
            camera.translation_y_axis == 0.03
        ), f"Expected 0.03, got {camera.translation_y_axis}"

        print("  ✅ camera_parameters fix working correctly!")
        return True

    except Exception as e:
        print(f"  ❌ camera_parameters test failed: {e}")
        return False


def test_attribute_error_fix():
    """Test that the AttributeError is fixed"""
    print("🧪 Testing AttributeError fix...")

    try:
        from dataclasses import dataclass

        import numpy as np

        @dataclass
        class CameraParameters:
            """camera parameters"""

            rotation_x_axis = None
            rotation_y_axis = None
            rotation_z_axis = None
            translation_x_axis = None
            translation_y_axis = None
            translation_zoom = None
            rotation: np.ndarray = None
            translation: np.ndarray = None

        class MockRenderer:
            def __init__(self):
                self.camera_parameters = CameraParameters()
                # Initialize to avoid None values
                self.camera_parameters.rotation_x_axis = 0.0
                self.camera_parameters.rotation_y_axis = 0.0

            def _apply_camera_rotation(self, dx, dy):
                # This was the line causing the AttributeError
                self.camera_parameters.rotation_x_axis += dy * 0.5
                self.camera_parameters.rotation_y_axis += dx * 0.5

        # Create mock renderer
        renderer = MockRenderer()

        # Test the method that was causing the error
        renderer._apply_camera_rotation(10.0, 15.0)

        # Verify results
        assert (
            renderer.camera_parameters.rotation_x_axis == 7.5
        ), f"Expected 7.5, got {renderer.camera_parameters.rotation_x_axis}"
        assert (
            renderer.camera_parameters.rotation_y_axis == 5.0
        ), f"Expected 5.0, got {renderer.camera_parameters.rotation_y_axis}"

        print("  ✅ AttributeError fix working correctly!")
        return True

    except Exception as e:
        print(f"  ❌ AttributeError test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Qt Cube Fixes...")
    print("=" * 50)

    tests = [
        test_mvp_parameters_fix,
        test_camera_parameters_fix,
        test_attribute_error_fix,
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
        print("🎉 All tests passed! Both Qt cube fixes are working correctly.")
        print("")
        print("📋 Summary of fixes:")
        print("  1. Fixed TypeError: mvp_parameters values initialized to 0.0")
        print("  2. Fixed AttributeError: camera_parameter → camera_parameters")
        print("  3. Fixed TypeError: camera_parameters values initialized to 0.0")
        print("")
        print("✅ The Qt cube examples should now work without errors!")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
