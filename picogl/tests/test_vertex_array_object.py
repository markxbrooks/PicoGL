"""
Unit tests for the VertexArrayObject class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.backend.modern.core.vertex.array.object.VertexArrayObject`
class, which manages OpenGL Vertex Array Objects (VAOs) in modern OpenGL rendering workflows.

The tests cover:

- Object initialization with and without handle parameter
- VAO binding/unbinding operations
- VBO management and attribute configuration
- EBO (Element Buffer Object) management
- Layout descriptor configuration
- Drawing operations with various modes
- Buffer cleanup and memory management
- Error handling and edge cases

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.backend.modern.core.vertex.array.object.VertexArrayObject
    - picogl.buffers.attributes.LayoutDescriptor

To run the tests::

    python -m unittest picogl.tests.test_vertex_array_object

"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from OpenGL.raw.GL._types import GL_FLOAT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_STATIC_DRAW

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.gpu.buffers.attributes import AttributeSpec, LayoutDescriptor


class TestVertexArrayObject(unittest.TestCase):
    """Test cases for VertexArrayObject class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_handle = 123
        self.test_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        self.test_indices = np.array([0, 1, 2], dtype=np.uint32)

        # Mock OpenGL functions to avoid context issues
        self.gl_patches = [
            patch("picogl.backend.modern.core.vertex.array.object.glBindVertexArray"),
            patch("picogl.backend.modern.core.vertex.array.object.glGenVertexArrays"),
            patch(
                "picogl.backend.modern.core.vertex.array.object.glDeleteVertexArrays"
            ),
            patch("picogl.backend.modern.core.vertex.array.object.glBindBuffer"),
            patch(
                "picogl.backend.modern.core.vertex.array.object.glEnableVertexAttribArray"
            ),
            patch(
                "picogl.backend.modern.core.vertex.array.object.glVertexAttribPointer"
            ),
            patch("picogl.backend.modern.core.vertex.array.object.gl_draw_arrays"),
            patch("picogl.backend.modern.core.vertex.array.object.gl_draw_elements"),
            patch(
                "picogl.backend.modern.core.vertex.array.object.enable_points_rendering_state"
            ),
            patch("picogl.backend.modern.core.vertex.array.object.gl_gen_safe"),
        ]

        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization_with_handle(self):
        """Test VertexArrayObject initialization with provided handle."""
        vao = VertexArrayObject(handle=self.mock_handle)

        self.assertEqual(vao.handle, self.mock_handle)
        self.assertFalse(vao._configured)
        self.assertEqual(vao.attributes, [])
        self.assertEqual(vao.vbos, [])
        self.assertEqual(vao.named_vbos, {})
        self.assertIsNone(vao.layout)

    def test_initialization_without_handle(self):
        """Test VertexArrayObject initialization without handle (auto-generate)."""
        # Mock glGenVertexArrays to return a handle
        with patch(
            "picogl.backend.modern.core.vertex.array.object.glGenVertexArrays"
        ) as mock_gen:
            with patch(
                "picogl.backend.modern.core.vertex.array.object.gl_gen_safe"
            ) as mock_gen_safe:
                mock_gen_safe.return_value = self.mock_handle
                vao = VertexArrayObject()

                self.assertEqual(vao.handle, self.mock_handle)
                mock_gen_safe.assert_called_once()

    def test_initialization_raises_error_when_no_context(self):
        """Test that initialization raises error when OpenGL context is not ready."""
        with patch(
            "picogl.backend.modern.core.vertex.array.object.glGenVertexArrays"
        ) as mock_gen:
            with patch(
                "picogl.backend.modern.core.vertex.array.object.gl_gen_safe"
            ) as mock_gen_safe:
                mock_gen.return_value = None
                mock_gen_safe.side_effect = TypeError(
                    "int() argument must be a string, a bytes-like object or a real number, not 'NoneType'"
                )

                with self.assertRaises(TypeError) as context:
                    VertexArrayObject()

                self.assertIn("int() argument must be a string", str(context.exception))

    def test_bind(self):
        """Test bind method."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.bind()
        # The bind call is already mocked in setUp

    def test_unbind(self):
        """Test unbind method."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.unbind()
        # The unbind call is already mocked in setUp

    def test_delete(self):
        """Test delete method."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.delete()
        # The delete call is already mocked in setUp

    def test_add_vbo(self):
        """Test add_vbo method."""
        with patch(
            "picogl.backend.modern.core.vertex.array.object.ModernVBO"
        ) as mock_vbo_class:
            mock_vbo = MagicMock()
            mock_vbo.handle = 456
            mock_vbo_class.return_value = mock_vbo

            vao = VertexArrayObject(handle=self.mock_handle)
            result = vao.add_vbo(
                index=0, data=self.test_data, size=3, dtype=GL_FLOAT, name="position"
            )

            # Verify VBO was created and configured
            mock_vbo_class.assert_called_once_with(handle=None)
            mock_vbo.bind.assert_called_once()
            mock_vbo.set_data.assert_called_once_with(self.test_data)
            mock_vbo.set_vertex_attributes.assert_called_once_with(
                index=0, data=self.test_data, size=3, dtype=GL_FLOAT
            )
            mock_vbo.configure.assert_called_once()

            # Verify VBO was added to internal lists
            self.assertEqual(len(vao.attributes), 1)
            self.assertEqual(len(vao.vbos), 1)
            self.assertEqual(vao.named_vbos["position"], mock_vbo)
            self.assertEqual(result, mock_vbo)

    def test_add_attribute(self):
        """Test add_attribute method."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vbo_handle = 789

        vao.add_attribute(
            index=1,
            vbo=vbo_handle,
            size=3,
            dtype=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        )

        # Verify attribute was added to the list
        self.assertEqual(len(vao.attributes), 1)
        expected_attr = (1, vbo_handle, 3, GL_FLOAT, False, 0, 0)
        self.assertEqual(vao.attributes[0], expected_attr)

    def test_add_ebo(self):
        """Test add_ebo method."""
        with patch(
            "picogl.backend.modern.core.vertex.array.object.ModernEBO"
        ) as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo_class.return_value = mock_ebo

            vao = VertexArrayObject(handle=self.mock_handle)
            result = vao.add_ebo(self.test_indices)

            # Verify EBO was created and configured
            mock_ebo_class.assert_called_once_with(data=self.test_indices)
            mock_ebo.bind.assert_called_once()
            mock_ebo.set_element_attributes.assert_called_once_with(
                data=self.test_indices,
                size=self.test_indices.nbytes,
                dtype=GL_STATIC_DRAW,
            )
            mock_ebo.configure.assert_called_once()

            # Verify EBO was stored
            self.assertEqual(vao.ebo, mock_ebo)
            self.assertEqual(result, mock_ebo)

    def test_set_ebo(self):
        """Test set_ebo method."""
        with patch(
            "picogl.backend.modern.core.vertex.array.object.ModernEBO"
        ) as mock_ebo_class:
            mock_ebo = MagicMock()
            mock_ebo_class.return_value = mock_ebo
            ebo_handle = 999

            vao = VertexArrayObject(handle=self.mock_handle)
            result = vao.set_ebo(ebo_handle)

            # Verify EBO was created with the handle
            mock_ebo_class.assert_called_once_with(handle=ebo_handle)
            mock_ebo.bind.assert_called_once()

            # Verify EBO was stored
            self.assertEqual(vao.ebo, mock_ebo)
            self.assertEqual(result, ebo_handle)

    def test_set_layout(self):
        """Test set_layout method with LayoutDescriptor."""
        # Create a mock layout descriptor
        attr_spec = AttributeSpec(
            name="position",
            index=0,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        )
        layout = LayoutDescriptor(attributes=[attr_spec])

        # Create mock VBO and EBO
        mock_vbo = MagicMock()
        mock_vbo._id = 100
        mock_ebo = MagicMock()
        mock_ebo._id = 200

        vao = VertexArrayObject(handle=self.mock_handle)
        vao.vao = mock_vbo  # Set vao to enable layout processing
        vao.vbo = mock_vbo
        vao.ebo = mock_ebo

        vao.set_layout(layout)

        # Verify layout was stored
        self.assertEqual(vao.layout, layout)
        self.assertTrue(vao._configured)

    def test_set_layout_with_none_vao(self):
        """Test set_layout method when vao is None."""
        layout = LayoutDescriptor(attributes=[])
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.vao = None

        vao.set_layout(layout)

        # Should return early without processing
        self.assertEqual(vao.layout, layout)

    def test_add_vbo_object(self):
        """Test add_vbo_object method for VBO management."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()

        # Test adding VBO with canonical name
        result = vao.add_vbo_object("position", mock_vbo)

        self.assertEqual(result, mock_vbo)
        self.assertEqual(vao.named_vbos["position"], mock_vbo)

        # Test adding VBO with alias
        mock_vbo2 = MagicMock()
        result2 = vao.add_vbo_object(
            "pos", mock_vbo2
        )  # "pos" should be an alias for "position"

        # Note: This test assumes NAME_ALIASES contains "pos" -> "position" mapping
        # The actual behavior depends on the NAME_ALIASES dictionary

    def test_get_vbo_object(self):
        """Test get_vbo_object method for VBO retrieval."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_vbo = MagicMock()

        vao.named_vbos["position"] = mock_vbo

        result = vao.get_vbo_object("position")
        self.assertEqual(result, mock_vbo)

        # Test with non-existent name
        result_none = vao.get_vbo_object("nonexistent")
        self.assertIsNone(result_none)

    def test_index_count_property(self):
        """Test index_count property."""
        vao = VertexArrayObject(handle=self.mock_handle)

        # Test with no EBO
        self.assertEqual(vao.index_count, 0)

        # Test with EBO containing data
        mock_ebo = MagicMock()
        mock_ebo.data = self.test_indices
        vao.ebo = mock_ebo

        self.assertEqual(vao.index_count, len(self.test_indices))

    def test_draw_with_arrays(self):
        """Test draw method with vertex arrays (no EBO)."""
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.ebo = None  # No EBO, should use glDrawArrays

        vao.draw(index_count=10, mode=GL_POINTS)
        # The draw calls are already mocked in setUp

    def test_draw_with_elements(self):
        """Test draw method with element arrays (EBO present)."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_ebo = MagicMock()
        mock_ebo.data = self.test_indices
        vao.ebo = mock_ebo

        vao.draw(index_count=5, mode=GL_POINTS)
        # The draw calls are already mocked in setUp

    def test_draw_with_auto_index_count(self):
        """Test draw method with automatic index count from EBO."""
        vao = VertexArrayObject(handle=self.mock_handle)
        mock_ebo = MagicMock()
        mock_ebo.data = self.test_indices
        vao.ebo = mock_ebo

        vao.draw()  # No index_count provided, should use EBO data length
        # The draw calls are already mocked in setUp

    def test_delete_buffers(self):
        """Test delete_buffers method."""
        with patch(
            "picogl.backend.modern.core.vertex.array.object.delete_buffer"
        ) as mock_delete:
            vao = VertexArrayObject(handle=self.mock_handle)

            # Add some mock VBOs
            mock_vbo1 = MagicMock()
            mock_vbo2 = MagicMock()
            vao.vbos = [mock_vbo1, mock_vbo2]

            # Add mock EBO
            mock_ebo = MagicMock()
            vao.ebo = mock_ebo

            vao.delete_buffers()

            # Verify VBOs were deleted
            self.assertEqual(mock_delete.call_count, 3)  # 2 VBOs + 1 EBO
            mock_delete.assert_any_call(mock_vbo1)
            mock_delete.assert_any_call(mock_vbo2)
            mock_delete.assert_any_call(mock_ebo)

            # Verify internal state was cleared
            self.assertEqual(len(vao.vbos), 0)
            self.assertIsNone(vao.ebo)
            self.assertEqual(len(vao.named_vbos), 0)

    def test_context_manager(self):
        """Test that VertexArrayObject can be used as a context manager."""
        vao = VertexArrayObject(handle=self.mock_handle)

        # Test that __enter__ and __exit__ methods exist
        self.assertTrue(hasattr(vao, "__enter__"))
        self.assertTrue(hasattr(vao, "__exit__"))

        # Test context manager usage
        with patch.object(vao, "bind") as mock_bind, patch.object(
            vao, "unbind"
        ) as mock_unbind:
            with vao as context_vao:
                self.assertEqual(context_vao, vao)
                mock_bind.assert_called_once()

            mock_unbind.assert_called_once()

    def test_repr_string(self):
        """Test string representation of VertexArrayObject."""
        vao = VertexArrayObject(handle=self.mock_handle)
        repr_str = repr(vao)

        self.assertIn("VertexArrayObject", repr_str)
        # The default repr doesn't include the handle, just test that it's a valid repr
        self.assertTrue(repr_str.startswith("<"))
        self.assertTrue(repr_str.endswith(">"))

    def test_error_handling_in_set_layout(self):
        """Test error handling in set_layout method."""
        layout = LayoutDescriptor(attributes=[])
        vao = VertexArrayObject(handle=self.mock_handle)
        vao.vao = MagicMock()  # Set vao to enable processing

        # Mock an exception during OpenGL calls
        with patch(
            "picogl.backend.modern.core.vertex.array.object.glBindVertexArray",
            side_effect=Exception("OpenGL error"),
        ):
            with patch("picogl.logger.Logger.error") as mock_log_error:
                vao.set_layout(layout)
                mock_log_error.assert_called_once()
                self.assertIn("error", mock_log_error.call_args[0][0])

    def test_error_handling_in_index_count(self):
        """Test error handling in index_count property."""
        vao = VertexArrayObject(handle=self.mock_handle)

        # Mock an exception
        with patch("picogl.logger.Logger.error") as mock_log_error:
            # Create a property that raises an exception
            class MockEBO:
                @property
                def data(self):
                    raise Exception("Data access error")

            vao.ebo = MockEBO()
            result = vao.index_count
            self.assertIsNone(
                result
            )  # Should return None on error (as per the actual implementation)
            mock_log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
