"""
Unit tests for the GLMesh class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.renderer.glmesh.GLMesh`
class, which manages GPU-resident mesh data and rendering.

The tests cover:

- Object initialization with various mesh data
- from_mesh_data class method
- GPU buffer upload and allocation
- OpenGL binding/unbinding operations
- Drawing operations
- Context manager functionality
- Resource cleanup and memory management
- Error handling and edge cases
- Data validation and type conversion

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.renderer.glmesh.GLMesh
    - picogl.renderer.meshdata.MeshData

To run the tests::

    python -m unittest picogl.tests.test_glmesh

"""

import unittest
from unittest.mock import MagicMock, patch, call

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT

from picogl.renderer.glmesh import GLMesh
from picogl.renderer.meshdata import MeshData


class TestGLMesh(unittest.TestCase):
    """Test cases for GLMesh class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test data
        self.test_vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        self.test_faces = np.array([0, 1, 2, 1, 3, 2], dtype=np.uint32)
        
        self.test_colors = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        self.test_normals = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        self.test_uvs = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0]
        ], dtype=np.float32)
        
        # Mock OpenGL functions to avoid context issues
        self.gl_patches = [
            patch('picogl.renderer.glmesh.glDrawElements'),
            patch('picogl.renderer.glmesh.delete_buffer_object'),
            # Mock VertexArrayObject and its methods
            patch('picogl.renderer.glmesh.VertexArrayObject'),
        ]
        
        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization_with_all_parameters(self):
        """Test GLMesh initialization with all parameters."""
        mesh = GLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        # Test data assignments
        np.testing.assert_array_equal(mesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(mesh.indices, self.test_faces)
        np.testing.assert_array_equal(mesh.colors, self.test_colors)
        np.testing.assert_array_equal(mesh.normals, self.test_normals)
        np.testing.assert_array_equal(mesh.uvs, self.test_uvs)
        
        # Test initial state
        self.assertIsNone(mesh.vao)
        self.assertEqual(mesh.index_count, 0)

    def test_initialization_with_minimal_parameters(self):
        """Test GLMesh initialization with only vertices and faces."""
        mesh = GLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces
        )
        
        # Test data assignments
        np.testing.assert_array_equal(mesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(mesh.indices, self.test_faces)
        
        # Test default values
        expected_colors = np.tile((0.0, 0.0, 1.0), (4, 1)).astype(np.float32)
        np.testing.assert_array_equal(mesh.colors, expected_colors)
        
        expected_normals = np.zeros_like(self.test_vertices)
        np.testing.assert_array_equal(mesh.normals, expected_normals)
        
        expected_uvs = np.zeros((4, 2), dtype=np.float32)
        np.testing.assert_array_equal(mesh.uvs, expected_uvs)
        
        # Test initial state
        self.assertIsNone(mesh.vao)
        self.assertEqual(mesh.index_count, 0)

    def test_initialization_with_empty_faces(self):
        """Test GLMesh initialization with empty faces raises error."""
        with self.assertRaises(ValueError) as context:
            GLMesh(
                vertices=self.test_vertices,
                faces=np.array([], dtype=np.uint32)
            )
        
        self.assertIn("GLMesh requires non-empty faces", str(context.exception))

    def test_initialization_with_none_faces(self):
        """Test GLMesh initialization with None faces raises error."""
        with self.assertRaises(TypeError) as context:
            GLMesh(
                vertices=self.test_vertices,
                faces=None
            )
        
        # The actual error is from numpy trying to convert None to uint32
        self.assertIn("int() argument must be a string", str(context.exception))

    def test_initialization_data_type_conversion(self):
        """Test that data is properly converted to correct types."""
        # Test with different input types
        int_vertices = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
        int_faces = np.array([0, 1], dtype=np.int32)
        
        mesh = GLMesh(vertices=int_vertices, faces=int_faces)
        
        # Should be converted to float32 and uint32
        self.assertEqual(mesh.vertices.dtype, np.float32)
        self.assertEqual(mesh.indices.dtype, np.uint32)

    def test_initialization_array_reshaping(self):
        """Test that arrays are properly reshaped."""
        # Test with 1D arrays
        vertices_1d = np.array([0, 0, 0, 1, 0, 0, 0, 1, 0], dtype=np.float32)
        faces_1d = np.array([0, 1, 2], dtype=np.uint32)
        
        mesh = GLMesh(vertices=vertices_1d, faces=faces_1d)
        
        # Should be reshaped to (N, 3) and (M,)
        self.assertEqual(mesh.vertices.shape, (3, 3))
        self.assertEqual(mesh.indices.shape, (3,))

    def test_from_mesh_data_with_all_attributes(self):
        """Test from_mesh_data with all MeshData attributes."""
        mesh_data = MeshData(
            vbo=self.test_vertices,
            ebo=self.test_faces,
            cbo=self.test_colors,
            nbo=self.test_normals,
            uvs=self.test_uvs
        )
        
        glmesh = GLMesh.from_mesh_data(mesh_data)
        
        # Test data assignments
        np.testing.assert_array_equal(glmesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(glmesh.indices, self.test_faces)
        np.testing.assert_array_equal(glmesh.colors, self.test_colors)
        np.testing.assert_array_equal(glmesh.normals, self.test_normals)
        np.testing.assert_array_equal(glmesh.uvs, self.test_uvs)

    def test_from_mesh_data_with_minimal_attributes(self):
        """Test from_mesh_data with minimal MeshData attributes."""
        mesh_data = MeshData(
            vbo=self.test_vertices,
            ebo=self.test_faces
        )
        
        glmesh = GLMesh.from_mesh_data(mesh_data)
        
        # Test data assignments
        np.testing.assert_array_equal(glmesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(glmesh.indices, self.test_faces)
        
        # Test default values
        expected_colors = np.tile((0.0, 0.0, 1.0), (4, 1)).astype(np.float32)
        np.testing.assert_array_equal(glmesh.colors, expected_colors)

    def test_from_mesh_data_without_uvs(self):
        """Test from_mesh_data without UVs attribute."""
        mesh_data = MeshData(
            vbo=self.test_vertices,
            ebo=self.test_faces,
            cbo=self.test_colors,
            nbo=self.test_normals
        )
        # Remove uvs attribute
        delattr(mesh_data, 'uvs')
        
        glmesh = GLMesh.from_mesh_data(mesh_data)
        
        # Should use default UVs
        expected_uvs = np.zeros((4, 2), dtype=np.float32)
        np.testing.assert_array_equal(glmesh.uvs, expected_uvs)

    def test_upload_first_time(self):
        """Test upload method for the first time."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VertexArrayObject
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        # Test VAO assignment
        self.assertEqual(mesh.vao, mock_vao)
        self.assertEqual(mesh.index_count, len(self.test_faces))
        
        # Test VAO methods were called
        mock_vao.add_vbo.assert_called()
        mock_vao.add_ebo.assert_called_once()

    def test_upload_already_uploaded(self):
        """Test upload method when already uploaded."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        # Upload again
        mesh.upload()
        
        # Should not create new VAO
        self.assertEqual(mesh.vao, mock_vao)

    def test_upload_with_uvs(self):
        """Test upload method with UVs."""
        mesh = GLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            uvs=self.test_uvs
        )
        
        # Mock VertexArrayObject
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        # Test that UV VBO was added
        calls = mock_vao.add_vbo.call_args_list
        uv_call_found = any(
            len(call[1]) > 0 and call[1].get('index') == 3 and call[1].get('size') == 2
            for call in calls
        )
        self.assertTrue(uv_call_found)

    def test_upload_without_uvs(self):
        """Test upload method without UVs."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Set UVs to None to test the condition
        mesh.uvs = None
        
        # Mock VertexArrayObject
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        # Test that UV VBO was not added (should have 3 calls: vertices, colors, normals)
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 3)  # Only vertices, colors, normals
        
        # Verify no UV call (index 3)
        uv_call_found = any(
            len(call[1]) > 0 and call[1].get('index') == 3
            for call in calls
        )
        self.assertFalse(uv_call_found)

    def test_bind_with_uploaded_mesh(self):
        """Test bind method with uploaded mesh."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        mesh.bind()
        
        # Test VAO context manager was called
        mock_vao.__enter__.assert_called_once()

    def test_bind_without_upload(self):
        """Test bind method without upload raises error."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        with self.assertRaises(RuntimeError) as context:
            mesh.bind()
        
        self.assertIn("GLMesh not uploaded", str(context.exception))

    def test_unbind_with_vao(self):
        """Test unbind method with VAO."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        mesh.unbind()
        
        # Test VAO context manager exit was called
        mock_vao.__exit__.assert_called_once_with(None, None, None)

    def test_unbind_without_vao(self):
        """Test unbind method without VAO."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should not raise error
        mesh.unbind()

    def test_delete_with_vao(self):
        """Test delete method with VAO."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        mesh.index_count = 10
        
        mesh.delete()
        
        # Test VAO was deleted and state was reset
        self.assertIsNone(mesh.vao)
        self.assertEqual(mesh.index_count, 0)

    def test_delete_without_vao(self):
        """Test delete method without VAO."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should not raise error
        mesh.delete()

    def test_context_manager(self):
        """Test that GLMesh can be used as a context manager."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        # Test context manager usage
        with mesh as context_mesh:
            self.assertEqual(context_mesh, mesh)
            mock_vao.__enter__.assert_called_once()
        
        mock_vao.__exit__.assert_called_once_with(None, None, None)

    def test_draw_with_uploaded_mesh(self):
        """Test draw method with uploaded mesh."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        mesh.index_count = len(self.test_faces)
        
        with patch('picogl.renderer.glmesh.glDrawElements') as mock_draw:
            mesh.draw()
        
        # Test VAO context manager was used
        mock_vao.__enter__.assert_called_once()
        mock_vao.__exit__.assert_called_once()
        
        # Test draw call was made
        mock_draw.assert_called_once_with(
            GL_TRIANGLES, 
            len(self.test_faces), 
            GL_UNSIGNED_INT, 
            mock_draw.call_args[0][3]  # ctypes.c_void_p(0)
        )

    def test_draw_without_upload(self):
        """Test draw method without upload handles error."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # The draw method catches exceptions and prints them instead of raising
        with patch('builtins.print') as mock_print:
            mesh.draw()
        
        # Should print the error message
        mock_print.assert_called_once()

    def test_draw_with_exception_handling(self):
        """Test draw method with exception handling."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO that raises exception
        mock_vao = MagicMock()
        mock_vao.__enter__.side_effect = Exception("OpenGL error")
        mesh.vao = mock_vao
        mesh.index_count = len(self.test_faces)
        
        # Should not raise exception, but print it
        with patch('builtins.print') as mock_print:
            mesh.draw()
        
        mock_print.assert_called_once()

    def test_vertex_count_calculation(self):
        """Test vertex count calculation."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Test initial count
        self.assertEqual(mesh.index_count, 0)
        
        # Test after upload
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        self.assertEqual(mesh.index_count, len(self.test_faces))

    def test_data_validation(self):
        """Test data validation and type checking."""
        # Test with valid data
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        self.assertEqual(mesh.vertices.shape[1], 3)  # Should be (N, 3)
        self.assertEqual(mesh.indices.ndim, 1)  # Should be 1D
        
        # Test with different vertex counts
        vertices_2 = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        faces_2 = np.array([0, 1], dtype=np.uint32)
        
        mesh_2 = GLMesh(vertices=vertices_2, faces=faces_2)
        self.assertEqual(mesh_2.vertices.shape[0], 2)
        self.assertEqual(mesh_2.colors.shape[0], 2)  # Colors should match vertex count

    def test_default_color_generation(self):
        """Test default colour generation."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should generate blue colors for all vertices
        expected_colors = np.tile((0.0, 0.0, 1.0), (4, 1)).astype(np.float32)
        np.testing.assert_array_equal(mesh.colors, expected_colors)

    def test_default_normal_generation(self):
        """Test default normal generation."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should generate zero normals
        expected_normals = np.zeros_like(self.test_vertices)
        np.testing.assert_array_equal(mesh.normals, expected_normals)

    def test_default_uv_generation(self):
        """Test default UV generation."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should generate zero UVs
        expected_uvs = np.zeros((4, 2), dtype=np.float32)
        np.testing.assert_array_equal(mesh.uvs, expected_uvs)

    def test_mesh_data_integration(self):
        """Test integration with MeshData class."""
        # Create MeshData
        mesh_data = MeshData.from_raw(
            vertices=self.test_vertices,
            indices=self.test_faces,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        # Create GLMesh from MeshData
        glmesh = GLMesh.from_mesh_data(mesh_data)
        
        # Test data consistency - GLMesh reshapes data to (N, 3) while MeshData keeps it flat
        np.testing.assert_array_equal(glmesh.vertices.reshape(-1), mesh_data.vbo)
        np.testing.assert_array_equal(glmesh.indices, mesh_data.ebo)
        np.testing.assert_array_equal(glmesh.colors.reshape(-1), mesh_data.cbo)
        np.testing.assert_array_equal(glmesh.normals.reshape(-1), mesh_data.nbo)
        np.testing.assert_array_equal(glmesh.uvs.reshape(-1), mesh_data.uvs)

    def test_upload_vbo_parameters(self):
        """Test that VBOs are added with correct parameters."""
        mesh = GLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        # Mock VertexArrayObject
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        # Test VBO calls
        calls = mock_vao.add_vbo.call_args_list
        
        # Should have 4 VBO calls (vertices, colors, normals, uvs)
        self.assertEqual(len(calls), 4)
        
        # Test vertex VBO (index 0, size 3)
        vertex_call = next(call for call in calls if call[1].get('index') == 0)
        self.assertEqual(vertex_call[1]['size'], 3)
        np.testing.assert_array_equal(vertex_call[1]['data'], self.test_vertices)
        
        # Test colour VBO (index 1, size 3)
        color_call = next(call for call in calls if call[1].get('index') == 1)
        self.assertEqual(color_call[1]['size'], 3)
        np.testing.assert_array_equal(color_call[1]['data'], self.test_colors)
        
        # Test normal VBO (index 2, size 3)
        normal_call = next(call for call in calls if call[1].get('index') == 2)
        self.assertEqual(normal_call[1]['size'], 3)
        np.testing.assert_array_equal(normal_call[1]['data'], self.test_normals)
        
        # Test UV VBO (index 3, size 2)
        uv_call = next(call for call in calls if call[1].get('index') == 3)
        self.assertEqual(uv_call[1]['size'], 2)
        np.testing.assert_array_equal(uv_call[1]['data'], self.test_uvs)

    def test_ebo_parameters(self):
        """Test that EBO is added with correct parameters."""
        mesh = GLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VertexArrayObject
        mock_vao = MagicMock()
        with patch('picogl.renderer.glmesh.VertexArrayObject', return_value=mock_vao):
            mesh.upload()
        
        # Test EBO call - verify it was called once
        mock_vao.add_ebo.assert_called_once()
        
        # Test the data parameter separately to avoid array comparison issues
        call_args = mock_vao.add_ebo.call_args
        np.testing.assert_array_equal(call_args[1]['data'], self.test_faces)


if __name__ == "__main__":
    unittest.main()
