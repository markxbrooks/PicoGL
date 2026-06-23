"""
Unit tests for the TextureRenderer class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.renderer.texture.TextureRenderer`
class, which provides specialized texture rendering functionality.

The tests cover:

- Object initialization and inheritance from ObjectRenderer
- Texture initialization and loading
- Path management and resolution
- UV coordinate handling and inversion
- Error handling and edge cases
- Data validation and type conversion

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.renderer.texture.TextureRenderer
    - picogl.renderer.meshdata.MeshData

To run the tests::

    python -m unittest picogl.tests.test_texture_renderer

"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import numpy as np

from picogl.renderer.meshdata import MeshData
from picogl.renderer.texture import TextureRenderer


class TestTextureRenderer(unittest.TestCase):
    """Test cases for TextureRenderer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test data
        self.test_vertices = np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
            dtype=np.float32,
        )

        self.test_colors = np.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 0.0]],
            dtype=np.float32,
        )

        self.test_normals = np.array(
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )

        self.test_uvs = np.array(
            [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32
        )

        # Create test MeshData
        self.test_mesh_data = MeshData.from_raw(
            vertices=self.test_vertices,
            colors=self.test_colors,
            normals=self.test_normals,
            uvs=self.test_uvs,
        )

        # Mock OpenGL functions and dependencies
        self.gl_patches = [
            patch("picogl.renderer.texture.GLContext"),
            patch("picogl.renderer.texture.MeshData"),
            patch("picogl.renderer.texture.ObjectRenderer"),
            patch("picogl.renderer.texture.TextureLoader"),
        ]

        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization_with_default_parameters(self):
        """Test TextureRenderer initialization with default parameters."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 123
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test basic properties
        self.assertEqual(renderer.context, mock_context)
        self.assertEqual(renderer.data, self.test_mesh_data)
        self.assertTrue(renderer.show_model)
        self.assertIsNone(renderer.base_dir)
        self.assertIsNone(renderer.glsl_dir)
        # resource_subdir is set to "tu02" by default in get_texture_filename
        self.assertEqual(renderer.resource_subdir, "tu02")

        # Test texture-related properties
        self.assertIsNotNone(renderer.texture_full_path)
        self.assertIsNotNone(renderer.resource_full_path)
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 123)

    def test_initialization_with_custom_parameters(self):
        """Test TextureRenderer initialization with custom parameters."""
        mock_context = MagicMock()
        base_dir = "/test/path"
        glsl_dir = "/test/glsl"

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 456
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                base_dir=base_dir,
                glsl_dir=glsl_dir,
                use_texture=True,
                texture_file="custom.tga",
                resource_subdir="tu03",
            )

        # Test basic properties
        self.assertEqual(renderer.base_dir, base_dir)
        self.assertEqual(renderer.glsl_dir, glsl_dir)
        self.assertEqual(renderer.base_path, Path(base_dir))

        # Test texture properties
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 456)

    def test_initialization_with_path_objects(self):
        """Test TextureRenderer initialization with Path objects."""
        mock_context = MagicMock()
        base_path = Path("/test/path")
        glsl_path = Path("/test/glsl")

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 789
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context,
                data=self.test_mesh_data,
                base_dir=base_path,
                glsl_dir=glsl_path,
            )

        # Test path handling
        self.assertEqual(renderer.base_dir, base_path)
        self.assertEqual(renderer.glsl_dir, glsl_path)
        self.assertEqual(renderer.base_path, base_path)

    def test_initialization_with_none_base_dir(self):
        """Test TextureRenderer initialization with None base_dir."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 111
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir=None
            )

        # Test that base_path is still created
        self.assertIsNone(renderer.base_dir)
        self.assertIsNotNone(renderer.base_path)

    def test_initialize_textures_with_normal_v_coords(self):
        """Test initialize_textures with normal V coordinates."""
        mock_context = MagicMock()
        original_uvs = self.test_uvs.copy()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 222
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test that UVs are not modified (compare flattened arrays)
        np.testing.assert_array_equal(
            renderer.data.texcoords.flatten(), original_uvs.flatten()
        )

        # Test texture setup
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 222)

    def test_initialize_textures_with_inversed_v_coords(self):
        """Test initialize_textures with inversed V coordinates."""
        mock_context = MagicMock()
        original_uvs = self.test_uvs.copy()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 333
            mock_texture.inversed_v_coords = True
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test that UVs are modified (V coordinates inverted)
        # The inversion works on the flattened array, so we need to work with flattened data
        expected_uvs_flat = original_uvs.flatten().copy()
        for index, _ in enumerate(expected_uvs_flat):
            if index % 2:  # Odd indices are V coordinates
                expected_uvs_flat[index] = 1.0 - expected_uvs_flat[index]

        np.testing.assert_array_equal(
            renderer.data.texcoords.flatten(), expected_uvs_flat
        )

        # Test texture setup
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 333)

    def test_get_texture_filename(self):
        """Test get_texture_filename method."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 444
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test that texture filename is set correctly
        expected_path = str(
            Path("/test/path").absolute() / "resources" / "tu02" / "uvtemplate.tga"
        )
        self.assertEqual(str(renderer.texture_full_path), expected_path)

        # Test that resource path is set
        expected_resource_path = Path("/test/path").absolute() / "resources" / "tu02"
        self.assertEqual(renderer.resource_full_path, expected_resource_path)

    def test_set_texture_filename(self):
        """Test set_texture_filename method."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 555
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test setting custom texture filename
        renderer.set_texture_filename("custom_texture.png")
        expected_path = (
            Path("/test/path").absolute() / "resources" / "tu02" / "custom_texture.png"
        )
        self.assertEqual(renderer.texture_full_path, expected_path)

    def test_set_texture_filename_with_none(self):
        """Test set_texture_filename method with None filename."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 666
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test setting None texture filename
        renderer.set_texture_filename(None)
        expected_path = (
            Path("/test/path").absolute() / "resources" / "tu02" / "default_texture.tga"
        )
        self.assertEqual(renderer.texture_full_path, expected_path)

    def test_set_resource_path(self):
        """Test set_resource_path method."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 777
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test setting custom resource path
        renderer.set_resource_path("/custom/base", "custom_subdir")
        expected_path = Path("/custom/base").absolute() / "resources" / "custom_subdir"
        self.assertEqual(renderer.resource_full_path, expected_path)

    def test_set_resource_path_with_path_object(self):
        """Test set_resource_path method with Path object."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 888
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test setting resource path with Path object
        custom_path = Path("/custom/base")
        renderer.set_resource_path(custom_path, "custom_subdir")
        expected_path = custom_path.absolute() / "resources" / "custom_subdir"
        self.assertEqual(renderer.resource_full_path, expected_path)

    def test_object_renderer_inheritance(self):
        """Test that TextureRenderer inherits from ObjectRenderer."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 999
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test inheritance
        from picogl.renderer.object import ObjectRenderer

        self.assertIsInstance(renderer, ObjectRenderer)

        # Test that ObjectRenderer methods are available
        self.assertTrue(hasattr(renderer, "initialize_shaders"))
        self.assertTrue(hasattr(renderer, "initialize"))
        self.assertTrue(hasattr(renderer, "render"))
        self.assertTrue(hasattr(renderer, "_draw_model"))

    def test_vertex_count_calculation(self):
        """Test vertex count calculation in initialization."""
        mock_context = MagicMock()

        # Test with different vertex data
        vertices_2d = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        mesh_data_2d = MeshData.from_raw(vertices=vertices_2d)

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 1000
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=mesh_data_2d)

        expected_vertex_count = len(vertices_2d.flatten()) // 3
        self.assertEqual(renderer.data.vertex_count, expected_vertex_count)

    def test_texture_loading_integration(self):
        """Test texture loading integration with TextureLoader."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 1111
            mock_texture.inversed_v_coords = True
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir="/test/path"
            )

        # Test that TextureLoader was called with correct path
        expected_path = str(
            Path("/test/path").absolute() / "resources" / "tu02" / "uvtemplate.tga"
        )
        mock_texture_loader.assert_called_once_with(expected_path)

        # Test texture assignment
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 1111)

    def test_uv_coordinate_inversion_edge_cases(self):
        """Test UV coordinate inversion with edge cases."""
        mock_context = MagicMock()

        # Test with UVs that have specific patterns
        test_uvs = np.array(
            [
                [0.0, 0.0],  # index 0: U=0, V=0
                [1.0, 0.5],  # index 1: U=1, V=0.5
                [0.5, 1.0],  # index 2: U=0.5, V=1
                [1.0, 1.0],  # index 3: U=1, V=1
            ],
            dtype=np.float32,
        )

        # Create a copy to avoid modification during test
        test_uvs_copy = test_uvs.copy()

        mesh_data_custom_uvs = MeshData.from_raw(
            vertices=self.test_vertices, uvs=test_uvs_copy
        )

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 2222
            mock_texture.inversed_v_coords = True
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=mesh_data_custom_uvs)

        # Test that only V coordinates (odd indices) are inverted
        # The inversion works on the flattened array, so we need to work with flattened data
        expected_uvs_flat = test_uvs.flatten().copy()
        for index, _ in enumerate(expected_uvs_flat):
            if index % 2:  # Odd indices are V coordinates
                expected_uvs_flat[index] = 1.0 - expected_uvs_flat[index]

        # Expected result: [0.  1.  1.  0.5 0.5 0.  1.  0. ]
        # This matches the actual behavior of the TextureRenderer
        np.testing.assert_array_equal(
            renderer.data.texcoords.flatten(), expected_uvs_flat
        )

    def test_draw_selection_method(self):
        """Test _draw_selection method exists and is callable."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 3333
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test that _draw_selection method exists and is callable
        self.assertTrue(hasattr(renderer, "_draw_selection"))
        self.assertTrue(callable(getattr(renderer, "_draw_selection")))

        # Test that it can be called without errors
        renderer._draw_selection()  # Should not raise an exception

    def test_initialization_with_minimal_mesh_data(self):
        """Test initialization with minimal mesh data."""
        minimal_mesh_data = MeshData.from_raw(vertices=self.test_vertices)

        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 4444
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=minimal_mesh_data)

        # Test that initialization succeeds with minimal data
        self.assertEqual(renderer.data, minimal_mesh_data)
        self.assertEqual(renderer.texture, mock_texture)
        self.assertEqual(renderer.context.texture_id, 4444)

    def test_path_absolute_conversion(self):
        """Test that paths are converted to absolute paths."""
        mock_context = MagicMock()
        relative_path = "relative/path"

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 5555
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(
                context=mock_context, data=self.test_mesh_data, base_dir=relative_path
            )

        # Test that base_path is created from relative path
        self.assertEqual(renderer.base_path, Path(relative_path))

        # Test that resource_full_path is absolute
        self.assertTrue(renderer.resource_full_path.is_absolute())

    def test_texture_gl_id_assignment(self):
        """Test that texture_gl_id is properly assigned to context."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 6666
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            renderer = TextureRenderer(context=mock_context, data=self.test_mesh_data)

        # Test that texture_gl_id is assigned to context
        self.assertEqual(mock_context.texture_id, 6666)

        # Test that texture is stored in renderer
        self.assertEqual(renderer.texture, mock_texture)

    def test_initialization_calls_initialize_textures(self):
        """Test that initialization calls initialize_textures."""
        mock_context = MagicMock()

        with patch("picogl.renderer.texture.TextureLoader") as mock_texture_loader:
            mock_texture = MagicMock()
            mock_texture.texture_gl_id = 7777
            mock_texture.inversed_v_coords = False
            mock_texture_loader.return_value = mock_texture

            with patch.object(
                TextureRenderer, "initialize_textures"
            ) as mock_init_textures:
                renderer = TextureRenderer(
                    context=mock_context, data=self.test_mesh_data
                )

        # Test that initialize_textures was called
        mock_init_textures.assert_called_once()


if __name__ == "__main__":
    unittest.main()
