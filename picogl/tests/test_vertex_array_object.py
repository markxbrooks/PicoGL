"""
Unit tests for the VertexArrayObject class in the PicoGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.backend.modern.core.vertex.array.object.VertexArrayObject`
class, which encapsulates OpenGL Vertex Array Objects (VAOs) in modern OpenGL rendering workflows.

The tests cover:

- Object initialization with and without handle parameter
- VAO binding/unbinding operations
- VBO management and registration
- Attribute configuration and management
- Element Buffer Object (EBO) handling
- Drawing operations
- Buffer cleanup and resource management
- Error handling and edge cases

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.backend.modern.core.vertex.array.object.VertexArrayObject

To run the tests::

    python -m unittest picogl.tests.test_vertex_array_object

"""

import unittest
from unittest.mock import MagicMock, patch, call
import numpy as np

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.buffers.attributes import LayoutDescriptor, AttributeSpec


class TestVertexArrayObject(unittest.TestCase):
    """Test cases for VertexArrayObject class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_handle = 123
        self.mock_vbo_handle = 456
        self.mock_ebo_handle = 789
        
        # Mock OpenGL functions
        self.gl_patches = {
            'glGenVertexArrays': patch('picogl.backend.modern.core.vertex.array.object.glGenVertexArrays'),
            'glBindVertexArray': patch('picogl.backend.modern.core.vertex.array.object.glBindVertexArray'),
            'glDeleteVertexArrays': patch('picogl.backend.modern.core.vertex.array.object.glDeleteVertexArrays'),
            'glDrawArrays': patch('picogl.backend.modern.core.vertex.array.object.glDrawArrays'),
            'glDrawElements': patch('picogl.backend.modern.core.vertex.array.object.glDrawElements'),
            'glEnableVertexAttribArray': patch('picogl.backend.modern.core.vertex.array.object.glEnableVertexAttribArray'),
            'glVertexAttribPointer': patch('picogl.backend.modern.core.vertex.array.object.glVertexAttribPointer'),
            'glBindBuffer': patch('picogl.backend.modern.core.vertex.array.object.glBindBuffer'),
        }
        
        # Start all patches
        for patch_obj in self.gl_patches.values():
            patch_obj.start()
        
        # Configure mock return values
        self.gl_patches['glGenVertexArrays'].return_value = [self.mock_handle]
        self.gl_patches['glBindVertexArray'].return_value = None
        self.gl_patches['glDeleteVertexArrays'].return_value = None
        self.gl_patches['glDrawArrays'].return_value = None
        self.gl_patches['glDrawElements'].return_value = None
        self.gl_patches['glEnableVertexAttribArray'].return_value = None
        self.gl_patches['glVertexAttribPointer'].return_value = None
        self.gl_patches['glBindBuffer'].return_value = None

    def tearDown(self):
        """Clean up test fixtures."""
        # Stop all patches
        for patch_obj in self.gl_patches.values():
            patch_obj.stop()

    def test_initialization_with_handle(self):
        """Test VAO initialization with provided handle."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertEqual(vao.handle, self.mock_handle)
        self.assertFalse(vao._configured)
        self.assertEqual(vao.attributes, [])
        self.assertEqual(vao.vbos, [])
        self.assertEqual(vao.named_vbos, {})
        self.assertIsNone(vao.layout)

    def test_initialization_without_handle(self):
        """Test VAO initialization without handle (auto-generation)."""
        vao = VertexArrayObject()
        
        self.assertEqual(vao.handle, self.mock_handle)
        self.gl_patches['glGenVertexArrays'].assert_called_once()

    def test_initialization_with_none_handle(self):
        """Test VAO initialization with None handle (auto-generation)."""
        vao = VertexArrayObject(handle=None)
        
        self.assertEqual(vao.handle, self.mock_handle)
        self.gl_patches['glGenVertexArrays'].assert_called_once()

    def test_initialization_raises_error_when_gl_not_available(self):
        """Test that initialization raises error when OpenGL context is not ready."""
        # Mock glGenVertexArrays to return None/False
        self.gl_patches['glGenVertexArrays'].return_value = None
        
        with self.assertRaises(RuntimeError) as context:
            VertexArrayObject()
        
        self.assertIn("glGenVertexArrays not available", str(context.exception))

    def test_bind_method(self):
        """Test VAO binding."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.bind()
        
        self.gl_patches['glBindVertexArray'].assert_called_with(self.mock_handle)

    def test_unbind_method(self):
        """Test VAO unbinding."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.unbind()
        
        self.gl_patches['glBindVertexArray'].assert_called_with(0)

    def test_delete_method(self):
        """Test VAO deletion."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.delete()
        
        self.gl_patches['glDeleteVertexArrays'].assert_called_with(1, [self.mock_handle])

    def test_add_vbo_with_data(self):
        """Test adding VBO with data."""
        vao = VertexArrayObject(handle=self.mock_handle)
        test_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernVBO') as mock_vbo_class:
            mock_vbo = MagicMock()
            mock_vbo.handle = self.mock_vbo_handle
            mock_vbo_class.return_value = mock_vbo
            
            result = vao.add_vbo(
                index=0,
                data=test_data,
                size=3,
                name="positions"
            )
            
            # Verify VBO was created and configured
            mock_vbo_class.assert_called_once_with(handle=None)
            mock_vbo.bind.assert_called_once()
            mock_vbo.set_data.assert_called_once_with(test_data)
            mock_vbo.set_vertex_attributes.assert_called_once()
            mock_vbo.configure.assert_called_once()
            
            # Verify VBO was added to VAO
            self.assertIn(mock_vbo, vao.vbos)
            self.assertIn("positions", vao.named_vbos)
            self.assertEqual(vao.named_vbos["positions"], mock_vbo)
            self.assertEqual(result, mock_vbo)

    def test_add_vbo_with_handle(self):
        """Test adding VBO with existing handle."""
        vao = VertexArrayObject(handle=self.mock_handle)
        test_data = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernVBO') as mock_vbo_class:
            mock_vbo = MagicMock()
            mock_vbo.handle = self.mock_vbo_handle
            mock_vbo_class.return_value = mock_vbo
            
            vao.add_vbo(
                index=1,
                data=test_data,
                size=3,
                handle=self.mock_vbo_handle
            )
            
            mock_vbo_class.assert_called_once_with(handle=self.mock_vbo_handle)

    def test_add_attribute(self):
        """Test adding vertex attribute."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        vao.add_attribute(
            index=0,
            vbo=self.mock_vbo_handle,
            size=3,
            dtype=0x1406,  # GL_FLOAT
            normalized=False,
            stride=0,
            offset=0
        )
        
        expected_attr = (0, self.mock_vbo_handle, 3, 0x1406, False, 0, 0)
        self.assertIn(expected_attr, vao.attributes)

    def test_add_ebo_with_data(self):
        """Test adding EBO with data."""
        vao = VertexArrayObject(handle=self.mock_handle)
        test_data = np.array([0, 1, 2, 3], dtype=np.uint32)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernEBO') as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo_class.return_value = mock_ebo
            
            result = vao.add_ebo(test_data)
            
            mock_ebo_class.assert_called_once_with(data=test_data)
            mock_ebo.bind.assert_called_once()
            mock_ebo.set_element_attributes.assert_called_once()
            mock_ebo.configure.assert_called_once()
            self.assertEqual(vao.ebo, mock_ebo)
            self.assertEqual(result, mock_ebo)

    def test_set_ebo_with_handle(self):
        """Test setting EBO with existing handle."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernEBO') as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo_class.return_value = mock_ebo
            
            result = vao.set_ebo(self.mock_ebo_handle)
            
            mock_ebo_class.assert_called_once_with(handle=self.mock_ebo_handle)
            mock_ebo.bind.assert_called_once()
            self.assertEqual(vao.ebo, mock_ebo)
            self.assertEqual(result, self.mock_ebo_handle)

    def test_index_count_property_with_ebo(self):
        """Test index_count property when EBO is present."""
        vao = VertexArrayObject(handle=self.mock_handle)
        test_data = np.array([0, 1, 2, 3], dtype=np.uint32)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernEBO') as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo.data = test_data
            mock_ebo_class.return_value = mock_ebo
            vao.add_ebo(test_data)
            
            self.assertEqual(vao.index_count, len(test_data))

    def test_index_count_property_without_ebo(self):
        """Test index_count property when no EBO is present."""
        vao = VertexArrayObject(handle=self.mock_handle)
        self.assertEqual(vao.index_count, 0)

    def test_index_count_property_with_ebo_no_data(self):
        """Test index_count property when EBO has no data."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernEBO') as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo.data = None
            mock_ebo_class.return_value = mock_ebo
            vao.add_ebo(np.array([]))
            
            self.assertEqual(vao.index_count, 0)

    def test_draw_with_ebo(self):
        """Test drawing with Element Buffer Object."""
        vao = VertexArrayObject(handle=self.mock_handle)
        test_data = np.array([0, 1, 2, 3], dtype=np.uint32)
        
        with patch('picogl.backend.modern.core.vertex.array.object.ModernEBO') as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo.data = test_data
            mock_ebo_class.return_value = mock_ebo
            vao.add_ebo(test_data)
            
            vao.draw(index_count=4, mode=0x0000)  # GL_POINTS
            
            self.gl_patches['glDrawElements'].assert_called_once()

    def test_draw_without_ebo(self):
        """Test drawing without Element Buffer Object."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        vao.draw(index_count=6, mode=0x0000)  # GL_POINTS
        
        self.gl_patches['glDrawArrays'].assert_called_once()

    def test_draw_with_points_mode(self):
        """Test drawing with GL_POINTS mode enables point rendering state."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        with patch('picogl.backend.modern.core.vertex.array.object.enable_points_rendering_state') as mock_enable_points:
            vao.draw(mode=0x0000)  # GL_POINTS
            mock_enable_points.assert_called_once()

    def test_draw_with_non_points_mode(self):
        """Test drawing with non-points mode doesn't enable point rendering state."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        with patch('picogl.backend.modern.core.vertex.array.object.enable_points_rendering_state') as mock_enable_points:
            vao.draw(mode=0x0004)  # GL_TRIANGLES
            mock_enable_points.assert_not_called()

    def test_set_layout_with_vbo(self):
        """Test setting layout with VBO."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        # Create mock VBO
        mock_vbo = MagicMock()
        mock_vbo._id = self.mock_vbo_handle
        vao.vbo = mock_vbo
        
        # Create layout descriptor
        attr_spec = AttributeSpec(
            name="position",
            index=0,
            size=3,
            type=0x1406,  # GL_FLOAT
            normalized=False,
            stride=0,
            offset=0
        )
        layout = LayoutDescriptor(attributes=[attr_spec])
        
        vao.set_layout(layout)
        
        # Verify VAO was bound
        self.gl_patches['glBindVertexArray'].assert_called_with(self.mock_handle)
        # Verify VBO was bound
        self.gl_patches['glBindBuffer'].assert_called()
        # Verify attributes were configured
        self.gl_patches['glEnableVertexAttribArray'].assert_called_with(0)
        self.gl_patches['glVertexAttribPointer'].assert_called()
        # Verify VAO was unbound
        self.assertEqual(self.gl_patches['glBindVertexArray'].call_count, 2)  # bind and unbind
        self.assertTrue(vao._configured)

    def test_set_layout_without_vbo(self):
        """Test setting layout without VBO."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.vao = None  # No VAO set
        
        attr_spec = AttributeSpec(
            name="position",
            index=0,
            size=3,
            type=0x1406,
            normalized=False,
            stride=0,
            offset=0
        )
        layout = LayoutDescriptor(attributes=[attr_spec])
        
        vao.set_layout(layout)
        
        # Should return early without doing anything
        self.gl_patches['glBindVertexArray'].assert_not_called()

    def test_set_layout_with_ebo(self):
        """Test setting layout with Element Buffer Object."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        # Create mock VBO and EBO
        mock_vbo = MagicMock()
        mock_vbo._id = self.mock_vbo_handle
        vao.vbo = mock_vbo
        
        mock_ebo = MagicMock()
        mock_ebo._id = self.mock_ebo_handle
        vao.ebo = mock_ebo
        
        attr_spec = AttributeSpec(
            name="position",
            index=0,
            size=3,
            type=0x1406,
            normalized=False,
            stride=0,
            offset=0
        )
        layout = LayoutDescriptor(attributes=[attr_spec])
        
        vao.set_layout(layout)
        
        # Verify EBO was bound
        ebo_calls = [call for call in self.gl_patches['glBindBuffer'].call_args_list 
                    if call[0][0] == 0x8893]  # GL_ELEMENT_ARRAY_BUFFER
        self.assertTrue(len(ebo_calls) > 0)

    def test_delete_buffers(self):
        """Test buffer deletion and cleanup."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        # Add some mock VBOs
        mock_vbo1 = MagicMock()
        mock_vbo2 = MagicMock()
        vao.vbos = [mock_vbo1, mock_vbo2]
        
        # Add named VBOs
        vao.named_vbos = {"position": mock_vbo1, "color": mock_vbo2}
        
        # Add mock EBO
        mock_ebo = MagicMock()
        vao.ebo = mock_ebo
        
        with patch('picogl.backend.modern.core.vertex.array.object.delete_buffer') as mock_delete:
            vao.delete_buffers()
            
            # Verify VBOs were deleted
            self.assertEqual(mock_delete.call_count, 3)  # 2 VBOs + 1 EBO
            self.assertEqual(len(vao.vbos), 0)
            self.assertEqual(len(vao.named_vbos), 0)
            self.assertIsNone(vao.ebo)

    def test_add_vbo_object(self):
        """Test adding VBO object by name."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()
        
        result = vao.add_vbo_object("position", mock_vbo)
        
        self.assertEqual(vao.named_vbos["position"], mock_vbo)
        self.assertEqual(result, mock_vbo)

    def test_add_vbo_object_with_alias(self):
        """Test adding VBO object with alias name."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()
        
        # Test with alias that should be normalized
        result = vao.add_vbo_object("pos", mock_vbo)
        
        # Should store under canonical name
        self.assertIn("position", vao.named_vbos)
        self.assertEqual(vao.named_vbos["position"], mock_vbo)
        self.assertEqual(result, mock_vbo)

    def test_get_vbo_object(self):
        """Test retrieving VBO object by name."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()
        vao.named_vbos["position"] = mock_vbo
        
        result = vao.get_vbo_object("position")
        self.assertEqual(result, mock_vbo)

    def test_get_vbo_object_with_alias(self):
        """Test retrieving VBO object with alias name."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()
        vao.named_vbos["position"] = mock_vbo
        
        result = vao.get_vbo_object("pos")
        self.assertEqual(result, mock_vbo)

    def test_get_vbo_object_not_found(self):
        """Test retrieving non-existent VBO object."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        result = vao.get_vbo_object("nonexistent")
        self.assertIsNone(result)

    def test_initialization_binds_vao(self):
        """Test that VAO is bound during initialization."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        # Should be called once during initialization
        self.gl_patches['glBindVertexArray'].assert_called_with(self.mock_handle)

    def test_attributes_list_initialization(self):
        """Test that attributes list is properly initialized."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertIsInstance(vao.attributes, list)
        self.assertEqual(len(vao.attributes), 0)

    def test_vbos_list_initialization(self):
        """Test that vbos list is properly initialized."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertIsInstance(vao.vbos, list)
        self.assertEqual(len(vao.vbos), 0)

    def test_named_vbos_dict_initialization(self):
        """Test that named_vbos dict is properly initialized."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertIsInstance(vao.named_vbos, dict)
        self.assertEqual(len(vao.named_vbos), 0)

    def test_configured_flag_initialization(self):
        """Test that _configured flag is properly initialized."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertFalse(vao._configured)

    def test_layout_initialization(self):
        """Test that layout is properly initialized."""
        vao = VertexArrayObject(handle=self.mock_handle)
        
        self.assertIsNone(vao.layout)


if __name__ == "__main__":
    unittest.main()
