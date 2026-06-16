"""
Unit tests for the LegacyGLMesh class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.renderer.legacy_glmesh.LegacyGLMesh`
class, which manages GPU-resident mesh data for legacy OpenGL compatibility.

The tests cover:

- Object initialization with various mesh data
- from_mesh_data class method
- GPU buffer upload and allocation with legacy VBOs
- Dynamic attribute generation for layout descriptors
- OpenGL binding/unbinding operations with legacy client states
- Drawing operations with legacy OpenGL functions
- Context manager functionality
- Resource cleanup and memory management
- Error handling and edge cases
- Data validation and type conversion

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.renderer.legacy_glmesh.LegacyGLMesh
    - picogl.renderer.meshdata.MeshData

To run the tests::

    python -m unittest picogl.tests.test_legacy_glmesh

"""

import unittest
from unittest.mock import MagicMock, patch, call

import numpy as np
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_COLOR_ARRAY, GL_VERTEX_ARRAY

from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.meshdata import MeshData


class TestLegacyGLMesh(unittest.TestCase):
    """Test cases for LegacyGLMesh class."""

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
            patch('picogl.renderer.legacy_glmesh.glDrawElements'),
            patch('picogl.renderer.legacy_glmesh.delete_buffer_object'),
            patch('picogl.renderer.legacy_glmesh.legacy_client_states'),
            patch('picogl.renderer.legacy_glmesh.create_layout'),
            patch('picogl.renderer.legacy_glmesh.VertexBufferGroup'),
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
        """Test LegacyGLMesh initialization with all parameters."""
        mesh = LegacyGLMesh(
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
        """Test LegacyGLMesh initialization with only vertices and faces."""
        mesh = LegacyGLMesh(
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
        """Test LegacyGLMesh initialization with empty faces raises error."""
        with self.assertRaises(ValueError) as context:
            LegacyGLMesh(
                vertices=self.test_vertices,
                faces=np.array([], dtype=np.uint32)
            )
        
        self.assertIn("GLMesh requires non-empty faces", str(context.exception))

    def test_initialization_data_type_conversion(self):
        """Test that data is properly converted to correct types."""
        # Test with different input types
        int_vertices = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int32)
        int_faces = np.array([0, 1], dtype=np.int32)
        
        mesh = LegacyGLMesh(vertices=int_vertices, faces=int_faces)
        
        # Should be converted to float32 and uint32
        self.assertEqual(mesh.vertices.dtype, np.float32)
        self.assertEqual(mesh.indices.dtype, np.uint32)

    def test_initialization_array_reshaping(self):
        """Test that arrays are properly reshaped."""
        # Test with 1D arrays
        vertices_1d = np.array([0, 0, 0, 1, 0, 0, 0, 1, 0], dtype=np.float32)
        faces_1d = np.array([0, 1, 2], dtype=np.uint32)
        
        mesh = LegacyGLMesh(vertices=vertices_1d, faces=faces_1d)
        
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
        
        legacy_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
        
        # Test data assignments
        np.testing.assert_array_equal(legacy_mesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(legacy_mesh.indices, self.test_faces)
        np.testing.assert_array_equal(legacy_mesh.colors, self.test_colors)
        np.testing.assert_array_equal(legacy_mesh.normals, self.test_normals)
        np.testing.assert_array_equal(legacy_mesh.uvs, self.test_uvs)

    def test_from_mesh_data_with_minimal_attributes(self):
        """Test from_mesh_data with minimal MeshData attributes."""
        mesh_data = MeshData(
            vbo=self.test_vertices,
            ebo=self.test_faces
        )
        
        legacy_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
        
        # Test data assignments
        np.testing.assert_array_equal(legacy_mesh.vertices, self.test_vertices)
        np.testing.assert_array_equal(legacy_mesh.indices, self.test_faces)
        
        # Test default values
        expected_colors = np.tile((0.0, 0.0, 1.0), (4, 1)).astype(np.float32)
        np.testing.assert_array_equal(legacy_mesh.colors, expected_colors)

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
        
        legacy_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
        
        # Should use default UVs
        expected_uvs = np.zeros((4, 2), dtype=np.float32)
        np.testing.assert_array_equal(legacy_mesh.uvs, expected_uvs)

    def test_generate_dynamic_attributes_without_uvs(self):
        """Test generate_dynamic_attributes without UVs."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        mesh.uvs = None  # Ensure no UVs
        
        attributes = mesh.generate_dynamic_attributes()
        
        # Should have 3 attributes: positions, colors, normals
        self.assertEqual(len(attributes), 3)
        
        # Test position attribute
        pos_attr = attributes[0]
        self.assertEqual(pos_attr.name, "positions")
        self.assertEqual(pos_attr.index, 0)
        self.assertEqual(pos_attr.size, 3)
        self.assertEqual(pos_attr.type, GL_FLOAT)
        
        # Test colour attribute
        color_attr = attributes[1]
        self.assertEqual(color_attr.name, "colors")
        self.assertEqual(color_attr.index, 1)
        self.assertEqual(color_attr.size, 3)
        self.assertEqual(color_attr.type, GL_FLOAT)
        
        # Test normal attribute
        normal_attr = attributes[2]
        self.assertEqual(normal_attr.name, "normals")
        self.assertEqual(normal_attr.index, 2)
        self.assertEqual(normal_attr.size, 3)
        self.assertEqual(normal_attr.type, GL_FLOAT)

    def test_generate_dynamic_attributes_with_uvs(self):
        """Test generate_dynamic_attributes with UVs."""
        mesh = LegacyGLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            uvs=self.test_uvs
        )
        
        attributes = mesh.generate_dynamic_attributes()
        
        # Should have 4 attributes: positions, colors, normals, uvs
        self.assertEqual(len(attributes), 4)
        
        # Test UV attribute
        uv_attr = attributes[3]
        self.assertEqual(uv_attr.name, "uvs")
        self.assertEqual(uv_attr.index, 3)
        self.assertEqual(uv_attr.size, 2)
        self.assertEqual(uv_attr.type, GL_FLOAT)

    def test_upload_first_time(self):
        """Test upload method for the first time."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock dependencies
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        # Test VAO assignment
        self.assertEqual(mesh.vao, mock_vao)
        self.assertEqual(mesh.index_count, len(self.test_faces))
        
        # Test VAO methods were called
        mock_vao.add_vbo.assert_called()
        mock_vao.add_ebo.assert_called_once()
        mock_vao.set_layout.assert_called_once_with(mock_layout)

    def test_upload_already_uploaded(self):
        """Test upload method when already uploaded."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        # Upload again
        mesh.upload()
        
        # Should not create new VAO
        self.assertEqual(mesh.vao, mock_vao)

    def test_upload_with_uvs(self):
        """Test upload method with UVs."""
        mesh = LegacyGLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            uvs=self.test_uvs
        )
        
        # Mock dependencies
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        # Test that UV VBO was added
        calls = mock_vao.add_vbo.call_args_list
        uv_call_found = any(
            len(call[1]) > 0 and call[1].get('name') == 'uvs' and call[1].get('size') == 2
            for call in calls
        )
        self.assertTrue(uv_call_found)

    def test_upload_without_uvs(self):
        """Test upload method without UVs."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        mesh.uvs = None  # Ensure no UVs
        
        # Mock dependencies
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        # Test that UV VBO was not added
        calls = mock_vao.add_vbo.call_args_list
        uv_call_found = any(
            len(call[1]) > 0 and call[1].get('name') == 'uvs'
            for call in calls
        )
        self.assertFalse(uv_call_found)

    def test_upload_vbo_parameters(self):
        """Test that VBOs are added with correct parameters."""
        mesh = LegacyGLMesh(
            vertices=self.test_vertices,
            faces=self.test_faces,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        # Mock dependencies
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        # Test VBO calls
        calls = mock_vao.add_vbo.call_args_list
        
        # Should have 4 VBO calls (vertices, colors, normals, uvs)
        self.assertEqual(len(calls), 4)
        
        # Test vertex VBO (name "vbo", size 3)
        vertex_call = next(call for call in calls if call[1].get('name') == 'vbo')
        self.assertEqual(vertex_call[1]['size'], 3)
        np.testing.assert_array_equal(vertex_call[1]['data'], self.test_vertices)
        
        # Test colour VBO (name "cbo", size 3)
        color_call = next(call for call in calls if call[1].get('name') == 'cbo')
        self.assertEqual(color_call[1]['size'], 3)
        np.testing.assert_array_equal(color_call[1]['data'], self.test_colors)
        
        # Test normal VBO (name "nbo", size 3)
        normal_call = next(call for call in calls if call[1].get('name') == 'nbo')
        self.assertEqual(normal_call[1]['size'], 3)
        np.testing.assert_array_equal(normal_call[1]['data'], self.test_normals)
        
        # Test UV VBO (name "uvs", size 2)
        uv_call = next(call for call in calls if call[1].get('name') == 'uvs')
        self.assertEqual(uv_call[1]['size'], 2)
        np.testing.assert_array_equal(uv_call[1]['data'], self.test_uvs)

    def test_ebo_parameters(self):
        """Test that EBO is added with correct parameters."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock dependencies
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        # Test EBO call
        mock_vao.add_ebo.assert_called_once()
        
        # Test the data parameter separately to avoid array comparison issues
        call_args = mock_vao.add_ebo.call_args
        np.testing.assert_array_equal(call_args[1]['data'], self.test_faces)

    def test_bind_with_uploaded_mesh(self):
        """Test bind method with uploaded mesh."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        mesh.bind()
        
        # Test VAO context manager was called
        mock_vao.__enter__.assert_called_once()

    def test_bind_without_upload(self):
        """Test bind method without upload raises error."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        with self.assertRaises(RuntimeError) as context:
            mesh.bind()
        
        self.assertIn("GLMesh not uploaded", str(context.exception))

    def test_unbind_with_vao(self):
        """Test unbind method with VAO."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO
        mock_vao = MagicMock()
        mesh.vao = mock_vao
        
        mesh.unbind()
        
        # Test VAO context manager exit was called
        mock_vao.__exit__.assert_called_once_with(None, None, None)

    def test_unbind_without_vao(self):
        """Test unbind method without VAO."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should not raise error
        mesh.unbind()

    def test_delete_with_vao(self):
        """Test delete method with VAO."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
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
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should not raise error
        mesh.delete()

    def test_context_manager(self):
        """Test that LegacyGLMesh can be used as a context manager."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
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
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO and its VBOs
        mock_vao = MagicMock()
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()
        mock_ebo = MagicMock()
        
        mock_vao.vbo = mock_vbo
        mock_vao.cbo = mock_cbo
        mock_vao.ebo = mock_ebo
        
        mesh.vao = mock_vao
        mesh.index_count = len(self.test_faces)
        
        with patch('picogl.renderer.legacy_glmesh.glDrawElements') as mock_draw:
            with patch('picogl.renderer.legacy_glmesh.legacy_client_states') as mock_client_states:
                mock_client_states.return_value.__enter__ = MagicMock()
                mock_client_states.return_value.__exit__ = MagicMock()
                
                mesh.draw()
        
        # Test draw call was made
        mock_draw.assert_called_once_with(
            GL_TRIANGLES, 
            len(self.test_faces), 
            GL_UNSIGNED_INT, 
            mock_draw.call_args[0][3]  # ctypes.c_void_p(0)
        )
        
        # Test legacy client states were used
        mock_client_states.assert_called_once_with(GL_VERTEX_ARRAY, GL_COLOR_ARRAY)

    def test_draw_with_custom_mode(self):
        """Test draw method with custom drawing mode."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO and its VBOs
        mock_vao = MagicMock()
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()
        mock_ebo = MagicMock()
        
        mock_vao.vbo = mock_vbo
        mock_vao.cbo = mock_cbo
        mock_vao.ebo = mock_ebo
        
        mesh.vao = mock_vao
        mesh.index_count = len(self.test_faces)
        
        with patch('picogl.renderer.legacy_glmesh.glDrawElements') as mock_draw:
            with patch('picogl.renderer.legacy_glmesh.legacy_client_states') as mock_client_states:
                mock_client_states.return_value.__enter__ = MagicMock()
                mock_client_states.return_value.__exit__ = MagicMock()
                
                mesh.draw(mode=GLDrawMode.TRIANGLES)
        
        # Test draw call was made with custom mode
        mock_draw.assert_called_once()

    def test_draw_without_upload(self):
        """Test draw method without upload handles error."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # The draw method catches exceptions and prints them instead of raising
        with patch('builtins.print') as mock_print:
            mesh.draw()
        
        # Should print the error message
        mock_print.assert_called_once()

    def test_draw_with_exception_handling(self):
        """Test draw method with exception handling."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO and its VBOs that raise exception
        mock_vao = MagicMock()
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()
        mock_ebo = MagicMock()
        
        mock_vao.vbo = mock_vbo
        mock_vao.cbo = mock_cbo
        mock_vao.ebo = mock_ebo
        
        # Make the legacy_client_states context manager raise an exception
        with patch('picogl.renderer.legacy_glmesh.legacy_client_states') as mock_client_states:
            mock_client_states.return_value.__enter__.side_effect = Exception("OpenGL error")
            mock_client_states.return_value.__exit__ = MagicMock()
            
            mesh.vao = mock_vao
            mesh.index_count = len(self.test_faces)
            
            # Should not raise exception, but print it
            with patch('builtins.print') as mock_print:
                mesh.draw()
            
            mock_print.assert_called_once()

    def test_vertex_count_calculation(self):
        """Test vertex count calculation."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Test initial count
        self.assertEqual(mesh.index_count, 0)
        
        # Test after upload
        mock_layout = MagicMock()
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.legacy_glmesh.create_layout', return_value=mock_layout):
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup', return_value=mock_vao):
                mesh.upload()
        
        self.assertEqual(mesh.index_count, len(self.test_faces))

    def test_data_validation(self):
        """Test data validation and type checking."""
        # Test with valid data
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        self.assertEqual(mesh.vertices.shape[1], 3)  # Should be (N, 3)
        self.assertEqual(mesh.indices.ndim, 1)  # Should be 1D
        
        # Test with different vertex counts
        vertices_2 = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        faces_2 = np.array([0, 1], dtype=np.uint32)
        
        mesh_2 = LegacyGLMesh(vertices=vertices_2, faces=faces_2)
        self.assertEqual(mesh_2.vertices.shape[0], 2)
        self.assertEqual(mesh_2.colors.shape[0], 2)  # Colors should match vertex count

    def test_default_color_generation(self):
        """Test default colour generation."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should generate blue colors for all vertices
        expected_colors = np.tile((0.0, 0.0, 1.0), (4, 1)).astype(np.float32)
        np.testing.assert_array_equal(mesh.colors, expected_colors)

    def test_default_normal_generation(self):
        """Test default normal generation."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Should generate zero normals
        expected_normals = np.zeros_like(self.test_vertices)
        np.testing.assert_array_equal(mesh.normals, expected_normals)

    def test_default_uv_generation(self):
        """Test default UV generation."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
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
        
        # Create LegacyGLMesh from MeshData
        legacy_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
        
        # Test data consistency - LegacyGLMesh reshapes data to (N, 3) while MeshData keeps it flat
        np.testing.assert_array_equal(legacy_mesh.vertices.reshape(-1), mesh_data.vbo)
        np.testing.assert_array_equal(legacy_mesh.indices, mesh_data.ebo)
        np.testing.assert_array_equal(legacy_mesh.colors.reshape(-1), mesh_data.cbo)
        np.testing.assert_array_equal(legacy_mesh.normals.reshape(-1), mesh_data.nbo)
        np.testing.assert_array_equal(legacy_mesh.uvs.reshape(-1), mesh_data.uvs)

    def test_legacy_client_states_integration(self):
        """Test integration with legacy client states."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        # Mock VAO and its VBOs
        mock_vao = MagicMock()
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()
        mock_ebo = MagicMock()
        
        mock_vao.vbo = mock_vbo
        mock_vao.cbo = mock_cbo
        mock_vao.ebo = mock_ebo
        
        mesh.vao = mock_vao
        mesh.index_count = len(self.test_faces)
        
        with patch('picogl.renderer.legacy_glmesh.legacy_client_states') as mock_client_states:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()
            
            mesh.draw()
            
            # Verify legacy client states were called with correct parameters
            mock_client_states.assert_called_once_with(GL_VERTEX_ARRAY, GL_COLOR_ARRAY)

    def test_attribute_spec_properties(self):
        """Test that generated attributes have correct properties."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        attributes = mesh.generate_dynamic_attributes()
        
        for attr in attributes:
            # All attributes should have required properties
            self.assertIsNotNone(attr.name)
            self.assertIsInstance(attr.index, int)
            self.assertIsInstance(attr.size, int)
            self.assertEqual(attr.type, GL_FLOAT)
            self.assertFalse(attr.normalized)
            self.assertEqual(attr.stride, 0)
            self.assertEqual(attr.offset, 0)

    def test_upload_layout_creation(self):
        """Test that layout is created with correct attributes."""
        mesh = LegacyGLMesh(vertices=self.test_vertices, faces=self.test_faces)
        
        with patch('picogl.renderer.legacy_glmesh.create_layout') as mock_create_layout:
            with patch('picogl.renderer.legacy_glmesh.VertexBufferGroup'):
                mesh.upload()
        
        # Test that create_layout was called
        mock_create_layout.assert_called_once()
        
        # Test that the attributes passed to create_layout are correct
        call_args = mock_create_layout.call_args[0][0]  # First positional argument
        # Should have 4 attributes: positions, colors, normals, uvs (UVs are always included)
        self.assertEqual(len(call_args), 4)
        
        # Test attribute names
        attr_names = [attr.name for attr in call_args]
        self.assertIn("positions", attr_names)
        self.assertIn("colors", attr_names)
        self.assertIn("normals", attr_names)
        self.assertIn("uvs", attr_names)


if __name__ == "__main__":
    unittest.main()
