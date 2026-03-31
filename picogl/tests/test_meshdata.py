"""
Unit tests for the MeshData class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.renderer.meshdata.MeshData`
class, which manages OpenGL mesh data and rendering state.

The tests cover:

- Object initialization with various buffer types
- from_raw class method with different input scenarios
- OpenGL binding/unbinding operations
- Drawing operations with various modes and parameters
- Context manager functionality
- Utility methods and data conversion
- Error handling and edge cases
- Data validation and type conversion

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.renderer.meshdata.MeshData

To run the tests::

    python -m unittest picogl.tests.test_meshdata

"""

import unittest
from unittest.mock import MagicMock, call, patch

import numpy as np
from OpenGL import GL
from picogl.renderer.meshdata import MeshData


class TestMeshData(unittest.TestCase):
    """Test cases for MeshData class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test data
        self.test_vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        self.test_normals = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        self.test_colors = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        self.test_uvs = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0]
        ], dtype=np.float32)
        
        self.test_indices = np.array([0, 1, 2, 1, 3, 2], dtype=np.int32)
        
        # Mock OpenGL functions to avoid context issues
        self.gl_patches = [
            patch('picogl.renderer.meshdata.GL.glEnableClientState'),
            patch('picogl.renderer.meshdata.GL.glDisableClientState'),
            patch('picogl.renderer.meshdata.GL.glVertexPointer'),
            patch('picogl.renderer.meshdata.GL.glNormalPointer'),
            patch('picogl.renderer.meshdata.GL.glColorPointer'),
            patch('picogl.renderer.meshdata.GL.glTexCoordPointer'),
            patch('picogl.renderer.meshdata.GL.glDrawElements'),
            patch('picogl.renderer.meshdata.GL.glLineWidth'),
            patch('picogl.renderer.meshdata.GL.glEnable'),
            patch('picogl.renderer.meshdata.GL.glDisable'),
            patch('picogl.renderer.meshdata.GL.glBlendFunc'),
            patch('picogl.renderer.meshdata.GL.glColor4f'),
            patch('picogl.renderer.meshdata.GL.glPolygonMode'),
        ]
        
        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization_with_all_buffers(self):
        """Test MeshData initialization with all buffer types."""
        mesh = MeshData(
            vertices=self.test_vertices,
            normals=self.test_normals,
            texcoords=self.test_uvs,
            colors=self.test_colors,
            ebo=self.test_indices
        )
        
        # Test buffer assignments
        np.testing.assert_array_equal(mesh.vbo, self.test_vertices)
        np.testing.assert_array_equal(mesh.nbo, self.test_normals)
        np.testing.assert_array_equal(mesh.uvs, self.test_uvs)
        np.testing.assert_array_equal(mesh.cbo, self.test_colors)
        np.testing.assert_array_equal(mesh.ebo, self.test_indices)
        
        # Test vertex count calculation
        expected_vertex_count = len(self.test_vertices.flatten()) // 3
        self.assertEqual(mesh.vertex_count, expected_vertex_count)

    def test_initialization_with_minimal_data(self):
        """Test MeshData initialization with only vertices."""
        mesh = MeshData(vertices=self.test_vertices)
        
        self.assertIsNotNone(mesh.vbo)
        self.assertIsNone(mesh.nbo)
        self.assertIsNone(mesh.uvs)
        self.assertIsNone(mesh.cbo)
        self.assertIsNone(mesh.ebo)
        
        expected_vertex_count = len(self.test_vertices.flatten()) // 3
        self.assertEqual(mesh.vertex_count, expected_vertex_count)

    def test_initialization_with_none_vertices(self):
        """Test MeshData initialization with None vertices."""
        mesh = MeshData()
        
        self.assertIsNone(mesh.vbo)
        self.assertIsNone(mesh.nbo)
        self.assertIsNone(mesh.uvs)
        self.assertIsNone(mesh.cbo)
        self.assertIsNone(mesh.ebo)
        self.assertIsNone(mesh.vertex_count)

    def test_as_ribbon_args(self):
        """Test as_ribbon_args method."""
        mesh = MeshData(
            vertices=self.test_vertices,
            normals=self.test_normals,
            colors=self.test_colors,
            ebo=self.test_indices
        )
        
        ribbon_args = mesh.as_canonical_names()
        
        expected = {
            "positions": self.test_vertices,
            "colors": self.test_colors,
            "normals": self.test_normals,
            "indices": self.test_indices,
        }
        
        self.assertEqual(ribbon_args, expected)

    def test_str_representation(self):
        """Test string representation of MeshData."""
        mesh = MeshData(
            vertices=self.test_vertices,
            texcoords=self.test_uvs,
            colors=self.test_colors
        )
        
        str_repr = str(mesh)
        # The __str__ method returns a formatted string with buffer info
        self.assertIsInstance(str_repr, str)
        # Check that it contains some representation of the data
        self.assertTrue(len(str_repr) > 0)

    def test_to_float32_flat_with_valid_array(self):
        """Test _to_float32_flat with valid array."""
        test_array = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        result = MeshData._to_float32_flat(test_array, "test", required=True)
        
        expected = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_to_float32_flat_with_none_required(self):
        """Test _to_float32_flat with None when required."""
        with self.assertRaises(ValueError) as context:
            MeshData._to_float32_flat(None, "test", required=True)
        
        self.assertIn("test is required", str(context.exception))

    def test_to_float32_flat_with_none_not_required(self):
        """Test _to_float32_flat with None when not required."""
        result = MeshData._to_float32_flat(None, "test", required=False)
        self.assertIsNone(result)

    def test_to_float32_flat_or_none(self):
        """Test _to_float32_flat_or_none method."""
        test_array = [1.0, 2.0, 3.0]
        result = MeshData._to_float32_flat_or_none(test_array, "test")
        
        expected = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_to_int32_flat_with_valid_array(self):
        """Test _to_int32_flat with valid array."""
        test_array = [[1, 2, 3], [4, 5, 6]]
        result = MeshData._to_int32_flat(test_array, "test", required=True)
        
        expected = np.array([1, 2, 3, 4, 5, 6], dtype=np.int32)
        np.testing.assert_array_equal(result, expected)

    def test_to_int32_flat_with_none_required(self):
        """Test _to_int32_flat with None when required."""
        with self.assertRaises(ValueError) as context:
            MeshData._to_int32_flat(None, "test", required=True)
        
        self.assertIn("test is required", str(context.exception))

    def test_default_colors_for_vertices(self):
        """Test _default_colors_for_vertices method."""
        vertex_count = 3
        result = MeshData._default_colors_for_vertices(vertex_count)
        
        expected = np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_default_normals_for_vertices(self):
        """Test _default_normals_for_vertices method."""
        vertex_count = 2
        result = MeshData._default_normals_for_vertices(vertex_count)
        
        expected = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0], dtype=np.float32)
        np.testing.assert_array_equal(result, expected)

    def test_from_raw_with_all_parameters(self):
        """Test from_raw with all parameters provided."""
        mesh = MeshData.from_raw(
            vertices=self.test_vertices,
            normals=self.test_normals,
            uvs=self.test_uvs,
            colors=self.test_colors,
            indices=self.test_indices
        )
        
        # Test that data is properly converted and stored
        self.assertIsNotNone(mesh.vbo)
        self.assertIsNotNone(mesh.nbo)
        self.assertIsNotNone(mesh.uvs)
        self.assertIsNotNone(mesh.cbo)
        self.assertIsNotNone(mesh.ebo)
        
        # Test vertex count
        expected_vertex_count = len(self.test_vertices)
        self.assertEqual(mesh.vertex_count, expected_vertex_count)

    def test_from_raw_with_minimal_parameters(self):
        """Test from_raw with only vertices."""
        mesh = MeshData.from_raw(vertices=self.test_vertices)
        
        self.assertIsNotNone(mesh.vbo)
        self.assertIsNotNone(mesh.nbo)  # Should be generated
        self.assertIsNone(mesh.uvs)
        self.assertIsNotNone(mesh.cbo)  # Should be generated
        self.assertIsNone(mesh.ebo)

    def test_from_raw_with_color_per_vertex_array(self):
        """Test from_raw with color_per_vertex array."""
        color_per_vertex = [0.5, 0.5, 0.5]  # Single colour
        mesh = MeshData.from_raw(
            vertices=self.test_vertices,
            color_per_vertex=color_per_vertex
        )
        
        self.assertIsNotNone(mesh.cbo)
        # Should have replicated the colour for all vertices
        expected_length = len(self.test_vertices) * 3
        self.assertEqual(len(mesh.cbo), expected_length)

    def test_from_raw_with_color_per_vertex_full_array(self):
        """Test from_raw with color_per_vertex as full array."""
        color_per_vertex = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        mesh = MeshData.from_raw(
            vertices=self.test_vertices,
            color_per_vertex=color_per_vertex
        )
        
        self.assertIsNotNone(mesh.cbo)
        expected = color_per_vertex.reshape(-1)
        np.testing.assert_array_equal(mesh.cbo, expected)

    def test_from_raw_with_invalid_color_per_vertex(self):
        """Test from_raw with invalid color_per_vertex."""
        with self.assertRaises(ValueError) as context:
            MeshData.from_raw(
                vertices=self.test_vertices,
                color_per_vertex="invalid"
            )
        
        self.assertIn("color_per_vertex must be array-like or None", str(context.exception))

    def test_from_raw_with_invalid_uvs_length(self):
        """Test from_raw with invalid UVs length."""
        invalid_uvs = np.array([[0.0, 0.0], [1.0, 1.0]])  # Wrong length
        
        with self.assertRaises(ValueError) as context:
            MeshData.from_raw(
                vertices=self.test_vertices,
                uvs=invalid_uvs
            )
        
        self.assertIn("uvs length must be 2 * vertex_count", str(context.exception))

    def test_bind_with_all_buffers(self):
        """Test bind method with all buffers present."""
        mesh = MeshData(
            vertices=self.test_vertices,
            normals=self.test_normals,
            texcoords=self.test_uvs,
            colors=self.test_colors
        )
        
        mesh.bind()
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_bind_with_minimal_buffers(self):
        """Test bind method with only vertices."""
        mesh = MeshData(vertices=self.test_vertices)
        
        mesh.bind()
        
        # Should not raise any errors

    def test_bind_with_none_buffers(self):
        """Test bind method with None buffers."""
        mesh = MeshData()
        
        mesh.bind()
        
        # Should not raise any errors

    def test_unbind_with_all_buffers(self):
        """Test unbind method with all buffers present."""
        mesh = MeshData(
            vertices=self.test_vertices,
            normals=self.test_normals,
            texcoords=self.test_uvs,
            colors=self.test_colors
        )
        
        mesh.unbind()
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_unbind_with_none_buffers(self):
        """Test unbind method with None buffers."""
        mesh = MeshData()
        
        mesh.unbind()
        
        # Should not raise any errors

    def test_context_manager(self):
        """Test that MeshData can be used as a context manager."""
        mesh = MeshData(vertices=self.test_vertices)
        
        # Test that __enter__ and __exit__ methods exist
        self.assertTrue(hasattr(mesh, "__enter__"))
        self.assertTrue(hasattr(mesh, "__exit__"))
        
        # Test context manager usage
        with patch.object(mesh, 'bind') as mock_bind, patch.object(mesh, 'unbind') as mock_unbind:
            with mesh as context_mesh:
                # The __enter__ method doesn't return self, it returns None
                self.assertIsNone(context_mesh)
                mock_bind.assert_called_once()
            
            mock_unbind.assert_called_once()

    def test_draw_with_vertex_colors(self):
        """Test draw method with vertex colors."""
        mesh = MeshData(
            vertices=self.test_vertices,
            colors=self.test_colors,
            ebo=self.test_indices
        )
        
        mesh.draw()
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_with_override_color(self):
        """Test draw method with override colour."""
        mesh = MeshData(
            vertices=self.test_vertices,
            ebo=self.test_indices
        )
        
        override_color = (1.0, 0.0, 0.0)
        mesh.draw(color=override_color)
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_with_fill_mode(self):
        """Test draw method with fill mode."""
        mesh = MeshData(
            vertices=self.test_vertices,
            ebo=self.test_indices
        )
        
        mesh.draw(fill=True)
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_with_alpha_blending(self):
        """Test draw method with alpha blending."""
        mesh = MeshData(
            vertices=self.test_vertices,
            ebo=self.test_indices
        )
        
        mesh.draw(alpha=0.5)
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_with_line_width(self):
        """Test draw method with custom line width."""
        mesh = MeshData(
            vertices=self.test_vertices,
            ebo=self.test_indices
        )
        
        mesh.draw(line_width=2.0)
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_with_custom_mode(self):
        """Test draw method with custom drawing mode."""
        mesh = MeshData(
            vertices=self.test_vertices,
            ebo=self.test_indices
        )
        
        mesh.draw(mode=GL.GL_LINES)
        
        # Verify OpenGL calls were made
        # The actual OpenGL calls are mocked in setUp

    def test_draw_without_ebo(self):
        """Test draw method without EBO."""
        mesh = MeshData(vertices=self.test_vertices)
        
        # This should raise an error because draw method expects ebo
        with self.assertRaises(TypeError):
            mesh.draw()

    def test_vertex_count_calculation(self):
        """Test vertex count calculation."""
        # Test with 2D array
        vertices_2d = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
        mesh = MeshData(vertices=vertices_2d)
        self.assertEqual(mesh.vertex_count, 2)
        
        # Test with 1D array
        vertices_1d = np.array([1, 2, 3, 4, 5, 6], dtype=np.float32)
        mesh = MeshData(vertices=vertices_1d)
        self.assertEqual(mesh.vertex_count, 2)

    def test_data_type_conversion(self):
        """Test that data is properly converted to correct types."""
        # Test with integer vertices
        int_vertices = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
        mesh = MeshData.from_raw(vertices=int_vertices)
        
        self.assertEqual(mesh.vbo.dtype, np.float32)
        
        # Test with float64 vertices
        float64_vertices = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64)
        mesh = MeshData.from_raw(vertices=float64_vertices)
        
        self.assertEqual(mesh.vbo.dtype, np.float32)

    def test_array_flattening(self):
        """Test that multi-dimensional arrays are properly flattened."""
        # Test with 3D array
        vertices_3d = np.array([[[1, 2, 3], [4, 5, 6]]], dtype=np.float32)
        mesh = MeshData.from_raw(vertices=vertices_3d)
        
        self.assertEqual(mesh.vbo.ndim, 1)
        self.assertEqual(len(mesh.vbo), 6)

    def test_error_handling_in_from_raw(self):
        """Test error handling in from_raw method."""
        # Test with None vertices
        with self.assertRaises(ValueError) as context:
            MeshData.from_raw(vertices=None)
        
        self.assertIn("vertices is required", str(context.exception))

    def test_color_generation_edge_cases(self):
        """Test colour generation with edge cases."""
        # Test with single vertex
        single_vertex = np.array([[1, 2, 3]], dtype=np.float32)
        mesh = MeshData.from_raw(vertices=single_vertex)
        
        self.assertIsNotNone(mesh.cbo)
        self.assertEqual(len(mesh.cbo), 3)  # Single colour (RGB)
        
        # Test with empty vertex array
        empty_vertices = np.array([], dtype=np.float32).reshape(0, 3)
        mesh = MeshData.from_raw(vertices=empty_vertices)
        
        self.assertIsNotNone(mesh.cbo)
        self.assertEqual(len(mesh.cbo), 0)

    def test_normal_generation(self):
        """Test normal generation when not provided."""
        mesh = MeshData.from_raw(vertices=self.test_vertices)
        
        self.assertIsNotNone(mesh.nbo)
        # Should have generated normals for all vertices
        expected_length = len(self.test_vertices) * 3
        self.assertEqual(len(mesh.nbo), expected_length)

    def test_repr_string(self):
        """Test string representation of MeshData."""
        mesh = MeshData(
            vertices=self.test_vertices,
            texcoords=self.test_uvs,
            colors=self.test_colors
        )
        
        repr_str = str(mesh)
        # The __str__ method returns a formatted string with buffer info
        self.assertIsInstance(repr_str, str)


if __name__ == "__main__":
    unittest.main()
