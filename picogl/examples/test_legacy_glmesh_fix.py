#!/usr/bin/env python3
"""
Test script to verify the LegacyGLMesh fix

This script tests that the LegacyGLMesh constructor properly handles
the case where faces is None and doesn't cause an AttributeError.
"""

import sys
from pathlib import Path

import numpy as np

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_legacy_glmesh_with_faces():
    """Test LegacyGLMesh with faces (should work)"""
    print("🧪 Testing LegacyGLMesh with faces...")

    try:
        from picogl.renderer.legacy_glmesh import LegacyGLMesh

        # Create test data
        vertices = np.array(
            [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]], dtype=np.float32
        )

        faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)

        colors = np.array(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]], dtype=np.float32
        )

        # Create LegacyGLMesh
        mesh = LegacyGLMesh(vertices=vertices, faces=faces, colors=colors)

        # Verify properties
        assert mesh.vertices.shape == (
            4,
            3,
        ), f"Expected (4, 3), got {mesh.vertices.shape}"
        assert mesh.indices.shape == (6,), f"Expected (6,), got {mesh.indices.shape}"
        assert mesh.colors.shape == (4, 3), f"Expected (4, 3), got {mesh.colors.shape}"

        print("  ✅ LegacyGLMesh with faces works correctly!")
        return True

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_legacy_glmesh_without_faces():
    """Test LegacyGLMesh without faces (should raise ValueError, not AttributeError)"""
    print("🧪 Testing LegacyGLMesh without faces...")

    try:
        from picogl.renderer.legacy_glmesh import LegacyGLMesh

        # Create test data
        vertices = np.array(
            [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]], dtype=np.float32
        )

        colors = np.array(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]], dtype=np.float32
        )

        # Try to create LegacyGLMesh without faces
        try:
            mesh = LegacyGLMesh(vertices=vertices, faces=None, colors=colors)
            print("  ❌ Unexpected: Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"  ✅ Expected ValueError: {e}")
            return True
        except AttributeError as e:
            print(f"  ❌ Unexpected AttributeError: {e}")
            return False

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_legacy_glmesh_empty_faces():
    """Test LegacyGLMesh with empty faces (should raise ValueError)"""
    print("🧪 Testing LegacyGLMesh with empty faces...")

    try:
        from picogl.renderer.legacy_glmesh import LegacyGLMesh

        # Create test data
        vertices = np.array(
            [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]], dtype=np.float32
        )

        colors = np.array(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0]], dtype=np.float32
        )

        # Try to create LegacyGLMesh with empty faces
        try:
            mesh = LegacyGLMesh(vertices=vertices, faces=np.array([]), colors=colors)
            print("  ❌ Unexpected: Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"  ✅ Expected ValueError: {e}")
            return True
        except AttributeError as e:
            print(f"  ❌ Unexpected AttributeError: {e}")
            return False

    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Testing LegacyGLMesh Fix...")
    print("=" * 50)

    tests = [
        test_legacy_glmesh_with_faces,
        test_legacy_glmesh_without_faces,
        test_legacy_glmesh_empty_faces,
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
        print("🎉 All tests passed! The LegacyGLMesh fix is working correctly.")
        print("")
        print("📋 Summary of the fix:")
        print("  1. Fixed AttributeError: self.indices now always exists")
        print("  2. When faces=None, self.indices is set to empty array")
        print("  3. ValueError is still raised for empty faces (as expected)")
        print("  4. No more AttributeError when accessing self.indices.size")
        print("")
        print("✅ The Qt cube example should now work with LegacyGLMesh!")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
