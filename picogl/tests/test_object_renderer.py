"""
Unit tests for the ObjectRenderer class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.renderer.object.ObjectRenderer`
class, which provides unified rendering for textured and untextured objects.

The tests cover:

- Object initialization with various parameters
- Shader initialization and compilation
- VAO and VBO setup for different data types
- Rendering pipeline and drawing operations
- Texture loading and binding
- Error handling and edge cases
- Data validation and type conversion

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.renderer.object.ObjectRenderer
    - picogl.renderer.meshdata.MeshData

To run the tests::

    python -m unittest picogl.tests.test_object_renderer

"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES
from picogl.renderer.meshdata import MeshData
from picogl.renderer.object import ObjectRenderer


class TestObjectRenderer(unittest.TestCase):
    """Test cases for ObjectRenderer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test data
        self.test_vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
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
        
        # Create test MeshData
        self.test_mesh_data = MeshData.from_raw(
            vertices=self.test_vertices,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        # Mock OpenGL functions and dependencies
        self.gl_patches = [
            patch('picogl.renderer.object.GLContext'),
            patch('picogl.renderer.object.VertexArrayObject'),
            patch('picogl.renderer.object.bind_texture_array'),
            patch('picogl.renderer.object.TextureLoader'),
            patch('picogl.renderer.object.log'),
        ]
        
        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization_without_texture(self):
        """Test ObjectRenderer initialization without texture."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        # Test basic properties
        self.assertEqual(renderer.context, mock_context)
        self.assertEqual(renderer.data, self.test_mesh_data)
        self.assertFalse(renderer.use_texture)
        self.assertIsNone(renderer.texture)
        self.assertTrue(renderer.show_model)
        self.assertIsNone(renderer.base_dir)
        self.assertIsNone(renderer.glsl_dir)
        self.assertEqual(renderer.resource_subdir, "tu02")
        
        # Test vertex count calculation
        expected_vertex_count = len(self.test_vertices.flatten()) // 3
        self.assertEqual(renderer.data.vertex_count, expected_vertex_count)

    def test_initialization_with_texture(self):
        """Test ObjectRenderer initialization with texture."""
        mock_context = MagicMock()
        mock_texture_loader = MagicMock()
        mock_texture_loader.texture_glid = 123
        
        with patch('picogl.renderer.object.TextureLoader', return_value=mock_texture_loader):
            renderer = ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                base_dir="/test/path",
                use_texture=True,
                texture_file="test_texture.tga",
                resource_subdir="tu03"
            )
        
        # Test basic properties
        self.assertEqual(renderer.context, mock_context)
        self.assertEqual(renderer.data, self.test_mesh_data)
        self.assertTrue(renderer.use_texture)
        self.assertEqual(renderer.texture, mock_texture_loader)
        self.assertEqual(renderer.base_dir, "/test/path")
        self.assertEqual(renderer.resource_subdir, "tu03")
        self.assertEqual(renderer.texture_file, "test_texture.tga")
        
        # Test texture ID assignment
        self.assertEqual(renderer.context.texture_id, 123)

    def test_initialization_with_path_objects(self):
        """Test ObjectRenderer initialization with Path objects."""
        mock_context = MagicMock()
        base_path = Path("/test/path")
        glsl_path = Path("/test/glsl")
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            base_dir=base_path,
            glsl_dir=glsl_path,
            use_texture=False
        )
        
        self.assertEqual(renderer.base_dir, base_path)
        self.assertEqual(renderer.glsl_dir, glsl_path)

    def test_initialization_with_none_context(self):
        """Test ObjectRenderer initialization with None context."""
        renderer = ObjectRenderer(
            context=None,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        self.assertIsNone(renderer.context)

    def test_initialize_shaders_with_existing_context(self):
        """Test initialize_shaders with existing context."""
        mock_context = MagicMock()
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        renderer.initialize_shaders()
        
        # Test shader program creation
        mock_context.create_shader_program.assert_called_once_with(
            vertex_source_file="vertex.glsl",
            fragment_source_file="fragment.glsl",
            glsl_dir=None
        )

    def test_initialize_shaders_with_custom_glsl_dir(self):
        """Test initialize_shaders with custom GLSL directory."""
        mock_context = MagicMock()
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            glsl_dir="/custom/glsl",
            use_texture=False
        )
        
        renderer.initialize_shaders()
        
        # Test shader program creation with custom directory
        mock_context.create_shader_program.assert_called_once_with(
            vertex_source_file="vertex.glsl",
            fragment_source_file="fragment.glsl",
            glsl_dir="/custom/glsl"
        )

    def test_initialize_shaders_with_none_context(self):
        """Test initialize_shaders with None context creates new one."""
        with patch('picogl.renderer.object.GLContext') as mock_gl_context_class:
            mock_new_context = MagicMock()
            mock_gl_context_class.return_value = mock_new_context
            
            renderer = ObjectRenderer(
                context=None,
                data=self.test_mesh_data,
                use_texture=False
            )
            
            renderer.initialize_shaders()
            
            # Test new context creation
            mock_gl_context_class.assert_called_once()
            self.assertEqual(renderer.context, mock_new_context)
            
            # Test shader program creation
            mock_new_context.create_shader_program.assert_called_once()

    def test_initialize_with_texture_and_uvs(self):
        """Test initialize method with texture and UVs."""
        mock_context = MagicMock()
        mock_context.vaos = {}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                use_texture=True
            )
            
            renderer.initialize()
        
        # Test VAO creation and VBO setup
        mock_vao.add_vbo.assert_called()
        
        # Test VAO assignment
        self.assertEqual(mock_context.vaos["model"], mock_vao)
        
        # Test VBO calls for texture mode
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 2)  # vertices + UVs
        
        # Test vertex VBO (index 0, size 3)
        vertex_call = next(call for call in calls if call[1].get('index') == 0)
        self.assertEqual(vertex_call[1]['index'], 0)
        self.assertEqual(vertex_call[1]['size'], 3)
        np.testing.assert_array_equal(vertex_call[1]['data'], self.test_mesh_data.vbo)
        
        # Test UV VBO (index 1, size 2)
        uv_call = next(call for call in calls if call[1].get('index') == 1)
        self.assertEqual(uv_call[1]['index'], 1)
        self.assertEqual(uv_call[1]['size'], 2)
        np.testing.assert_array_equal(uv_call[1]['data'], self.test_mesh_data.texcoords)

    def test_initialize_without_texture_with_colors_and_normals(self):
        """Test initialize method without texture, with colors and normals."""
        mock_context = MagicMock()
        mock_context.vaos = {}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                use_texture=False
            )
            
            renderer.initialize()
        
        # Test VAO creation and VBO setup
        mock_vao.add_vbo.assert_called()
        
        # Test VAO assignment
        self.assertEqual(mock_context.vaos["model"], mock_vao)
        
        # Test VBO calls for colour/normal mode
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 3)  # vertices + colors + normals
        
        # Test vertex VBO (index 0, size 3)
        vertex_call = next(call for call in calls if call[1].get('index') == 0)
        self.assertEqual(vertex_call[1]['index'], 0)
        self.assertEqual(vertex_call[1]['size'], 3)
        
        # Test colour VBO (index 1, size 3)
        color_call = next(call for call in calls if call[1].get('index') == 1)
        self.assertEqual(color_call[1]['index'], 1)
        self.assertEqual(color_call[1]['size'], 3)
        np.testing.assert_array_equal(color_call[1]['data'], self.test_mesh_data.cbo)
        
        # Test normal VBO (index 2, size 3)
        normal_call = next(call for call in calls if call[1].get('index') == 2)
        self.assertEqual(normal_call[1]['index'], 2)
        self.assertEqual(normal_call[1]['size'], 3)
        np.testing.assert_array_equal(normal_call[1]['data'], self.test_mesh_data.nbo)

    def test_initialize_without_texture_without_colors(self):
        """Test initialize method without texture and without colors."""
        # Create mesh data without colors
        mesh_data_no_colors = MeshData.from_raw(
            vertices=self.test_vertices,
            normals=self.test_normals,
            uvs=self.test_uvs
        )
        
        mock_context = MagicMock()
        mock_context.vaos = {}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=mesh_data_no_colors,
                use_texture=False
            )
            
            renderer.initialize()
        
        # Test VBO calls - ObjectRenderer always adds colors and normals when not using texture
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 3)  # vertices + colors + normals
        
        # Test that colors VBO was added (ObjectRenderer behavior)
        color_calls = [call for call in calls if call[1].get('index') == 1 and call[1].get('size') == 3]
        self.assertEqual(len(color_calls), 1)

    def test_initialize_with_existing_vaos(self):
        """Test initialize method with existing VAOs dictionary."""
        mock_context = MagicMock()
        mock_context.vaos = {"existing": "vao"}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                use_texture=False
            )
            
            renderer.initialize()
        
        # Test that existing VAOs are preserved
        self.assertIn("existing", mock_context.vaos)
        self.assertIn("model", mock_context.vaos)

    def test_render_with_show_model_true(self):
        """Test render method with show_model=True."""
        mock_context = MagicMock()
        mock_vao = MagicMock()
        mock_shader = MagicMock()
        mock_context.vaos = {"model": mock_vao}
        mock_context.shader = mock_shader
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        with patch.object(renderer, '_draw_model') as mock_draw_model:
            with patch.object(renderer, '_finalize_render') as mock_finalize:
                renderer.render()
        
        mock_draw_model.assert_called_once()
        mock_finalize.assert_called_once()

    def test_render_with_show_model_false(self):
        """Test render method with show_model=False."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        renderer.show_model = False
        
        with patch.object(renderer, '_draw_model') as mock_draw_model:
            with patch.object(renderer, '_finalize_render') as mock_finalize:
                renderer.render()
        
        mock_draw_model.assert_not_called()
        mock_finalize.assert_called_once()

    def test_draw_model_without_texture(self):
        """Test _draw_model method without texture."""
        mock_context = MagicMock()
        mock_vao = MagicMock()
        mock_shader = MagicMock()
        mock_context.vaos = {"model": mock_vao}
        mock_context.shader = mock_shader
        mock_context.mvp_matrix = np.eye(4)
        mock_context.model_matrix = np.eye(4)
        mock_context.eye_np = np.array([0, 0, 5])
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        with patch.object(mock_vao, 'draw') as mock_draw:
            renderer._draw_model()
        
        # Test shader context manager usage
        mock_shader.__enter__.assert_called_once()
        mock_shader.__exit__.assert_called_once()
        
        # Test VAO context manager usage
        mock_vao.__enter__.assert_called_once()
        mock_vao.__exit__.assert_called_once()
        
        # Test uniform setting
        mock_shader.uniform.assert_any_call("mvp_matrix", mock_context.mvp_matrix)
        mock_shader.uniform.assert_any_call("model_matrix", mock_context.model_matrix)
        mock_shader.uniform.assert_any_call("viewPos", mock_context.eye_np)
        
        # Test draw call
        mock_draw.assert_called_once_with(mode=GL_TRIANGLES, index_count=renderer.data.vertex_count)

    def test_draw_model_with_texture(self):
        """Test _draw_model method with texture."""
        mock_context = MagicMock()
        mock_vao = MagicMock()
        mock_shader = MagicMock()
        mock_texture = MagicMock()
        mock_context.vaos = {"model": mock_vao}
        mock_context.shader = mock_shader
        mock_context.mvp_matrix = np.eye(4)
        mock_context.model_matrix = np.eye(4)
        mock_context.eye_np = np.array([0, 0, 5])
        mock_context.texture_id = 123
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=True
        )
        renderer.texture = mock_texture
        
        with patch.object(mock_vao, 'draw') as mock_draw:
            with patch('picogl.renderer.object.bind_texture_array') as mock_bind_texture:
                renderer._draw_model()
        
        # Test texture binding
        mock_bind_texture.assert_called_once_with(123)
        
        # Test texture uniform
        mock_shader.uniform.assert_any_call("texture0", 0)

    def test_draw_model_without_texture_object(self):
        """Test _draw_model method with use_texture=True but no texture object."""
        mock_context = MagicMock()
        mock_vao = MagicMock()
        mock_shader = MagicMock()
        mock_context.vaos = {"model": mock_vao}
        mock_context.shader = mock_shader
        mock_context.mvp_matrix = np.eye(4)
        mock_context.model_matrix = np.eye(4)
        mock_context.eye_np = np.array([0, 0, 5])
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=True
        )
        renderer.texture = None  # No texture object
        
        with patch.object(mock_vao, 'draw') as mock_draw:
            with patch('picogl.renderer.object.bind_texture_array') as mock_bind_texture:
                renderer._draw_model()
        
        # Test that texture binding was not called
        mock_bind_texture.assert_not_called()
        
        # Test that texture uniform was not set
        texture_uniform_calls = [call for call in mock_shader.uniform.call_args_list 
                                if call[0][0] == "texture0"]
        self.assertEqual(len(texture_uniform_calls), 0)

    def test_vertex_count_calculation(self):
        """Test vertex count calculation in initialization."""
        mock_context = MagicMock()
        
        # Test with different vertex data
        vertices_2d = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        mesh_data_2d = MeshData.from_raw(vertices=vertices_2d)
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=mesh_data_2d,
            use_texture=False
        )
        
        expected_vertex_count = len(vertices_2d.flatten()) // 3
        self.assertEqual(renderer.data.vertex_count, expected_vertex_count)

    def test_texture_loading_with_valid_path(self):
        """Test texture loading with valid path."""
        mock_context = MagicMock()
        mock_texture_loader = MagicMock()
        mock_texture_loader.texture_glid = 456
        
        with patch('picogl.renderer.object.TextureLoader', return_value=mock_texture_loader):
            renderer = ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                base_dir="/test/path",
                use_texture=True,
                texture_file="test.tga",
                resource_subdir="tu04"
            )
        
        # Test texture loader creation
        self.assertEqual(renderer.texture, mock_texture_loader)
        
        # Test texture ID assignment
        self.assertEqual(renderer.context.texture_id, 456)

    def test_texture_loading_without_texture_file(self):
        """Test texture loading without texture file."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            base_dir="/test/path",
            use_texture=True,
            texture_file=None
        )
        
        # Should not create texture loader
        self.assertIsNone(renderer.texture)

    def test_texture_loading_without_base_dir(self):
        """Test texture loading without base directory."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            base_dir=None,
            use_texture=True,
            texture_file="test.tga"
        )
        
        # Should use current directory as base
        self.assertIsNotNone(renderer.texture)

    def test_renderer_base_inheritance(self):
        """Test that ObjectRenderer inherits from RendererBase."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        # Test inheritance
        from picogl.renderer import RendererBase
        self.assertIsInstance(renderer, RendererBase)

    def test_initialization_with_minimal_mesh_data(self):
        """Test initialization with minimal mesh data (only vertices)."""
        minimal_mesh_data = MeshData.from_raw(vertices=self.test_vertices)
        
        mock_context = MagicMock()
        mock_context.vaos = {}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=minimal_mesh_data,
                use_texture=False
            )
            
            renderer.initialize()
        
        # Should have vertex VBO + colors + normals (ObjectRenderer always adds them)
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 3)  # vertices + colors + normals
        
        # Test vertex VBO
        vertex_call = calls[0]
        self.assertEqual(vertex_call[1]['index'], 0)
        self.assertEqual(vertex_call[1]['size'], 3)

    def test_initialization_with_texture_but_no_uvs(self):
        """Test initialization with texture enabled but no UVs in mesh data."""
        mesh_data_no_uvs = MeshData.from_raw(
            vertices=self.test_vertices,
            colors=self.test_colors,
            normals=self.test_normals
        )
        
        mock_context = MagicMock()
        mock_context.vaos = {}
        mock_vao = MagicMock()
        
        with patch('picogl.renderer.object.VertexArrayObject', return_value=mock_vao):
            renderer = ObjectRenderer(
                context=mock_context,
                data=mesh_data_no_uvs,
                use_texture=True
            )
            
            renderer.initialize()
        
        # Should fall back to colour/normal mode
        calls = mock_vao.add_vbo.call_args_list
        self.assertEqual(len(calls), 3)  # vertices + colors + normals
        
        # Test that UV VBO was not added
        uv_calls = [call for call in calls if call[1].get('index') == 1 and call[1].get('size') == 2]
        self.assertEqual(len(uv_calls), 0)

    def test_log_parameter_calls(self):
        """Test that log.parameter is called for texture usage."""
        mock_context = MagicMock()
        
        with patch('picogl.renderer.object.log') as mock_log:
            ObjectRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                use_texture=True
            )
        
        # Test log parameter call
        mock_log.parameter.assert_called_once_with("Using texture", True)

    def test_finalize_render_inheritance(self):
        """Test that _finalize_render is inherited from RendererBase."""
        mock_context = MagicMock()
        
        renderer = ObjectRenderer(
            context=mock_context,
            data=self.test_mesh_data,
            use_texture=False
        )
        
        # Test that _finalize_render method exists
        self.assertTrue(hasattr(renderer, '_finalize_render'))
        self.assertTrue(callable(getattr(renderer, '_finalize_render')))


if __name__ == "__main__":
    unittest.main()
