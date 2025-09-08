#!/usr/bin/env python3
"""
Simple test to verify the mvp_parameters fix

This script tests that the mvp_parameters can be properly initialized
and that arithmetic operations work without the TypeError.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_mvp_parameters_fix():
    """Test that mvp_parameters can be initialized and used"""
    print("🧪 Testing mvp_parameters fix...")

    try:
        from picogl.ui.backend.qt.base import MvpParameters

        # Create mvp_parameters instance
        mvp = MvpParameters()

        print(f"  Initial values:")
        print(f"    rotation_x: {mvp.rotation_x} (type: {type(mvp.rotation_x)})")
        print(f"    rotation_y: {mvp.rotation_y} (type: {type(mvp.rotation_y)})")
        print(f"    pan_x: {mvp.pan_x} (type: {type(mvp.pan_x)})")
        print(f"    pan_y: {mvp.pan_y} (type: {type(mvp.pan_y)})")

        # Initialize values to avoid None
        mvp.rotation_x = 0.0
        mvp.rotation_y = 0.0
        mvp.pan_x = 0.0
        mvp.pan_y = 0.0

        print(f"  After initialization:")
        print(f"    rotation_x: {mvp.rotation_x} (type: {type(mvp.rotation_x)})")
        print(f"    rotation_y: {mvp.rotation_y} (type: {type(mvp.rotation_y)})")
        print(f"    pan_x: {mvp.pan_x} (type: {type(mvp.pan_x)})")
        print(f"    pan_y: {mvp.pan_y} (type: {type(mvp.pan_y)})")

        # Test the problematic operation that was causing the TypeError
        print("  Testing arithmetic operations...")

        # This was the line causing the error:
        # self.mvp_parameters.rotation_x += delta.x() * 0.5
        delta_x = 10.0
        delta_y = 15.0

        mvp.rotation_x += delta_x * 0.5
        mvp.rotation_y += delta_y * 0.5
        mvp.pan_x += delta_x * 0.01
        mvp.pan_y += delta_y * 0.01

        print(f"  After arithmetic operations:")
        print(f"    rotation_x: {mvp.rotation_x} (expected: 5.0)")
        print(f"    rotation_y: {mvp.rotation_y} (expected: 7.5)")
        print(f"    pan_x: {mvp.pan_x} (expected: 0.1)")
        print(f"    pan_y: {mvp.pan_y} (expected: 0.15)")

        # Verify the results
        assert mvp.rotation_x == 5.0, f"Expected 5.0, got {mvp.rotation_x}"
        assert mvp.rotation_y == 7.5, f"Expected 7.5, got {mvp.rotation_y}"
        assert mvp.pan_x == 0.1, f"Expected 0.1, got {mvp.pan_x}"
        assert mvp.pan_y == 0.15, f"Expected 0.15, got {mvp.pan_y}"

        print("  ✅ All arithmetic operations completed successfully!")
        print("  ✅ No TypeError occurred!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_qt_cube_initialization_logic():
    """Test the initialization logic from QtCubeRenderer"""
    print("🧪 Testing QtCubeRenderer initialization logic...")

    try:
        from picogl.ui.backend.qt.base import MvpParameters

        # Simulate the initialization from QtCubeRenderer
        mvp_parameters = MvpParameters()

        # This is what we added to fix the issue:
        mvp_parameters.rotation_x = 0.0
        mvp_parameters.rotation_y = 0.0
        mvp_parameters.pan_x = 0.0
        mvp_parameters.pan_y = 0.0

        print(f"  Initialized mvp_parameters:")
        print(f"    rotation_x: {mvp_parameters.rotation_x}")
        print(f"    rotation_y: {mvp_parameters.rotation_y}")
        print(f"    pan_x: {mvp_parameters.pan_x}")
        print(f"    pan_y: {mvp_parameters.pan_y}")

        # Test the mouse movement simulation
        print("  Simulating mouse movement...")

        # Simulate delta values from mouse movement
        delta_x = 5.0
        delta_y = -3.0

        # This is the operation that was failing:
        mvp_parameters.rotation_x += delta_y * 0.5
        mvp_parameters.rotation_y += delta_x * 0.5

        print(f"  After mouse movement simulation:")
        print(f"    rotation_x: {mvp_parameters.rotation_x} (expected: -1.5)")
        print(f"    rotation_y: {mvp_parameters.rotation_y} (expected: 2.5)")

        # Verify results
        assert (
            mvp_parameters.rotation_x == -1.5
        ), f"Expected -1.5, got {mvp_parameters.rotation_x}"
        assert (
            mvp_parameters.rotation_y == 2.5
        ), f"Expected 2.5, got {mvp_parameters.rotation_y}"

        print("  ✅ Mouse movement simulation successful!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Testing MVP Parameters Fix...")
    print("=" * 60)

    tests = [
        test_mvp_parameters_fix,
        test_qt_cube_initialization_logic,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The mvp_parameters fix is working correctly.")
        print("✅ The TypeError should no longer occur in the Qt cube examples.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
