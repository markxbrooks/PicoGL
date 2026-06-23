"""
Unit tests for the VertexBufferGroup class in the PicoGL OpenGL backend.

This module contains a comprehensive suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.gpu.buffers.vertex.legacy.VertexBufferGroup`
class, which manages legacy OpenGL vertex buffer objects and mimics VAO functionality.

The tests cover:

- Object initialization and setup
- VBO management and attribute configuration
- EBO (Element Buffer Object) management
- Layout descriptor configuration
- Drawing operations with various modes
- Buffer cleanup and memory management
- Error handling and edge cases
- Legacy client state management

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for OpenGL function mocking
    - numpy for test data
    - picogl.gpu.buffers.vertex.legacy.VertexBufferGroup
    - picogl.buffers.attributes.LayoutDescriptor

To run the tests::

    python -m unittest picogl.tests.test_vertex_buffer_group

"""

import ctypes
import unittest
from unittest.mock import MagicMock, call, patch

import numpy as np
from OpenGL.raw.GL._types import GL_FLOAT, GL_UNSIGNED_INT
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POINTS, GL_TRIANGLES
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER

from picogl.backend.gl.enums import GLDrawMode
from picogl.gpu.buffers.attributes import AttributeSpec, LayoutDescriptor
from picogl.gpu.buffers.vertex.aliases import VertexBufferRole
from picogl.gpu.buffers.vertex.legacy import VertexBufferGroup
from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType


class TestVertexBufferGroup(unittest.TestCase):
    """Test cases for VertexBufferGroup class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        self.test_indices = np.array([0, 1, 2], dtype=np.uint32)
        self.test_colors = np.array(
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32
        )

        # Mock OpenGL functions to avoid context issues
        self.gl_patches = [
            patch("picogl.gpu.buffers.vertex.legacy.glDrawArrays"),
            patch("picogl.gpu.buffers.vertex.legacy.glDrawElements"),
            patch("picogl.gpu.buffers.vertex.legacy.glBindBuffer"),
            patch("picogl.gpu.buffers.vertex.legacy.glVertexPointer"),
            patch("picogl.gpu.buffers.vertex.legacy.glColorPointer"),
            patch("picogl.gpu.buffers.vertex.legacy.glNormalPointer"),
            patch("picogl.gpu.buffers.vertex.legacy.gl_enableClientState"),
            patch("picogl.gpu.buffers.vertex.legacy.legacy_client_states"),
            patch("picogl.gpu.buffers.vertex.legacy.delete_buffer_object"),
            patch("OpenGL.gl.glGenBuffers", return_value=1),
            patch("OpenGL.gl.glBufferData"),
        ]

        # Start all patches
        for patch_obj in self.gl_patches:
            patch_obj.start()

    def tearDown(self):
        """Clean up after each test method."""
        # Stop all patches
        for patch_obj in self.gl_patches:
            patch_obj.stop()

    def test_initialization(self):
        """Test VertexBufferGroup initialization."""
        vbg = VertexBufferGroup()

        # Test initial state
        self.assertEqual(vbg.handle, 0)
        self.assertIsNone(vbg.vao)
        self.assertIsNone(vbg.vbo)
        self.assertIsNone(vbg.cbo)
        self.assertIsNone(vbg.nbo)
        self.assertIsNone(vbg.ebo)
        self.assertIsNone(vbg.layout)
        self.assertEqual(vbg.named_vbos, {})

        # Test VBO classes mapping
        expected_classes = [
            VBOType.VBO,
            VBOType.CBO,
            VBOType.EBO,
            VBOType.NBO,
        ]
        for class_name in expected_classes:
            self.assertIn(class_name, vbg.vbo_classes)

    def test_add_vbo_object(self):
        """Test add_vbo_object method for VBO management."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()
        mock_vbo._id = 123

        # Test adding VBO with canonical name
        result = vbg.add_vbo_object("position", mock_vbo)

        self.assertEqual(result, mock_vbo)
        self.assertEqual(vbg.named_vbos["position"], mock_vbo)

        # Test adding VBO with alias (if NAME_ALIASES contains mappings)
        mock_vbo2 = MagicMock()
        mock_vbo2._id = 456
        result2 = vbg.add_vbo_object("pos", mock_vbo2)

        self.assertEqual(result2, mock_vbo2)

    def test_get_vbo_object(self):
        """Test get_vbo_object method for VBO retrieval."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()

        vbg.named_vbos["position"] = mock_vbo

        result = vbg.get_vbo_object("position")
        self.assertEqual(result, mock_vbo)

        # Test with non-existent name
        result_none = vbg.get_vbo_object("nonexistent")
        self.assertIsNone(result_none)

    def test_index_count_property(self):
        """Test index_count property."""
        vbg = VertexBufferGroup()

        # Test with no EBO
        self.assertEqual(vbg.index_count, 0)

        # Test with EBO containing data
        mock_ebo = MagicMock()
        mock_ebo.data = self.test_indices
        vbg.ebo = mock_ebo

        self.assertEqual(vbg.index_count, len(self.test_indices))

        # Test with EBO but no data attribute
        mock_ebo_no_data = MagicMock()
        del mock_ebo_no_data.data  # Remove data attribute
        vbg.ebo = mock_ebo_no_data

        self.assertEqual(vbg.index_count, 0)

    def test_add_vbo(self):
        """Test add_vbo method with different buffer types."""
        vbg = VertexBufferGroup()

        # Mock the get_buffer_class method to return a mock class
        mock_vbo_class = MagicMock()
        mock_vbo = MagicMock()
        mock_vbo_class.return_value = mock_vbo

        with patch.object(vbg, "get_buffer_class", return_value=mock_vbo_class):
            # Test adding position VBO with default parameters
            result = vbg.add_vbo(VBOType.VBO, data=self.test_data)

            # Verify get_buffer_class was called
            vbg.get_buffer_class.assert_called_once_with(VBOType.VBO)

            # Verify VBO was created and added with default parameters
            mock_vbo_class.assert_called_once_with(
                data=self.test_data, size=3, handle=None, dtype=GL_FLOAT
            )
            self.assertIs(result, vbg)
            self.assertIs(vbg.named_vbos[VertexBufferRole.VBO], mock_vbo)

    def test_add_vbo_with_custom_parameters(self):
        """Test add_vbo method with custom parameters."""
        vbg = VertexBufferGroup()

        # Mock the get_buffer_class method to return a mock class
        mock_vbo_class = MagicMock()
        mock_vbo = MagicMock()
        mock_vbo_class.return_value = mock_vbo

        with patch.object(vbg, "get_buffer_class", return_value=mock_vbo_class):
            # Test adding VBO with custom parameters
            custom_handle = 123
            custom_size = 4
            custom_dtype = GL_UNSIGNED_INT

            result = vbg.add_vbo(
                VBOType.VBO,
                data=self.test_data,
                size=custom_size,
                handle=custom_handle,
                dtype=custom_dtype,
            )

            # Verify get_buffer_class was called
            vbg.get_buffer_class.assert_called_once_with(VBOType.VBO)

            # Verify VBO was created with custom parameters
            mock_vbo_class.assert_called_once_with(
                data=self.test_data,
                size=custom_size,
                handle=custom_handle,
                dtype=custom_dtype,
            )
            self.assertIs(result, vbg)
            self.assertIs(vbg.named_vbos[VertexBufferRole.VBO], mock_vbo)

    def test_add_vbo_invalid_parameters(self):
        """Test add_vbo method with invalid parameters."""
        vbg = VertexBufferGroup()

        # Test with None data
        with self.assertRaises(ValueError):
            vbg.add_vbo(VBOType.VBO, data=None)

        # Test with size <= 0
        with self.assertRaises(ValueError):
            vbg.add_vbo(VBOType.VBO, data=self.test_data, size=0)

        with self.assertRaises(ValueError):
            vbg.add_vbo(VBOType.VBO, data=self.test_data, size=-1)

    def test_add_ebo(self):
        """Test add_ebo method."""
        vbg = VertexBufferGroup()

        # Mock the EBO class in the vbo_classes dictionary
        mock_ebo_class = MagicMock()
        mock_ebo = MagicMock()
        mock_ebo_class.return_value = mock_ebo

        # Replace the EBO class in vbo_classes
        original_ebo_class = vbg.vbo_classes[VBOType.EBO]
        vbg.vbo_classes[VBOType.EBO] = mock_ebo_class

        try:
            vbg.add_ebo(VBOType.EBO, data=self.test_indices)

            mock_ebo_class.assert_called_once_with(data=self.test_indices)
            self.assertEqual(vbg.named_vbos[VBOType.EBO], mock_ebo)
        finally:
            # Restore original class
            vbg.vbo_classes[VBOType.EBO] = original_ebo_class

    def test_get_buffer_class(self):
        """Test get_buffer_class method."""
        vbg = VertexBufferGroup()

        # Test known buffer types
        self.assertEqual(
            vbg.get_buffer_class(VBOType.VBO), vbg.vbo_classes[VBOType.VBO]
        )
        self.assertEqual(
            vbg.get_buffer_class(VBOType.CBO), vbg.vbo_classes[VBOType.CBO]
        )
        self.assertEqual(
            vbg.get_buffer_class(VBOType.EBO), vbg.vbo_classes[VBOType.EBO]
        )
        self.assertEqual(
            vbg.get_buffer_class(VBOType.NBO), vbg.vbo_classes[VBOType.NBO]
        )

        # Test unknown buffer type (should return default)
        self.assertEqual(vbg.get_buffer_class("unknown"), vbg.vbo_classes[VBOType.VBO])

    def test_draw_with_arrays(self):
        """Test draw method with vertex arrays."""
        vbg = VertexBufferGroup()

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states, patch(
            "picogl.gpu.buffers.vertex.legacy.glDrawArrays"
        ) as mock_draw_arrays:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw(index_count=10, mode=GLDrawMode.POINTS)

            mock_draw_arrays.assert_called_once_with(GLDrawMode.POINTS, 0, 10)
            mock_client_states.assert_called_once_with(
                GL_VERTEX_ARRAY, GL_COLOR_ARRAY, GL_NORMAL_ARRAY
            )

    def test_draw_with_auto_index_count(self):
        """Test draw method with automatic index count."""
        vbg = VertexBufferGroup()

        mock_ebo = MagicMock()
        mock_ebo.data = self.test_indices
        vbg.ebo = mock_ebo

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states, patch(
            "picogl.gpu.buffers.vertex.legacy.glDrawArrays"
        ) as mock_draw_arrays:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw(mode=GLDrawMode.POINTS)

            mock_draw_arrays.assert_called_once_with(
                GLDrawMode.POINTS, 0, len(self.test_indices)
            )

    def test_draw_elements(self):
        """Test draw_elements method."""
        vbg = VertexBufferGroup()

        mock_ebo = MagicMock()
        mock_ebo._id = 123
        mock_ebo.handle = 123
        vbg.ebo = mock_ebo

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states, patch(
            "picogl.gpu.buffers.vertex.legacy.glDrawElements"
        ) as mock_draw_elements:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw_elements(count=5, mode=GLDrawMode.TRIANGLES)

            mock_draw_elements.assert_called_once()
            mock_client_states.assert_called_once_with(
                GL_VERTEX_ARRAY, GL_COLOR_ARRAY, GL_NORMAL_ARRAY
            )

    def test_draw_elements_without_ebo(self):
        """Test draw_elements method without EBO raises error."""
        vbg = VertexBufferGroup()

        with self.assertRaises(RuntimeError) as context:
            vbg.draw_elements()

        self.assertIn("No element buffer (EBO) bound", str(context.exception))

    def test_draw_elements_with_auto_count(self):
        """Test draw_elements method with automatic count."""
        vbg = VertexBufferGroup()

        mock_ebo = MagicMock()
        mock_ebo._id = 123
        mock_ebo.handle = 123
        mock_ebo.data = self.test_indices
        vbg.ebo = mock_ebo

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states, patch(
            "picogl.gpu.buffers.vertex.legacy.glDrawElements"
        ) as mock_draw_elements:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw_elements()

            mock_draw_elements.assert_called_once()

    def test_set_layout(self):
        """Test set_layout method."""
        vbg = VertexBufferGroup()
        layout = LayoutDescriptor(attributes=[])

        vbg.set_layout(layout)

        self.assertEqual(vbg.layout, layout)

    def test_bind_with_layout(self):
        """Test bind method with layout."""
        vbg = VertexBufferGroup()

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
        vbg.layout = layout

        # Add mock VBO
        mock_vbo = MagicMock()
        mock_vbo._id = 123
        vbg.named_vbos["position"] = mock_vbo

        vbg.bind()

        # The bind method calls glBindBuffer and glVertexAttribPointer
        # which are already mocked in setUp, so we just verify no errors occurred

    def test_bind_without_layout(self):
        """Test bind method without layout."""
        vbg = VertexBufferGroup()

        # Should return early without processing
        vbg.bind()
        # No assertions needed - should not raise any errors

    def test_bind_with_missing_vbo(self):
        """Test bind method with missing VBO in layout."""
        vbg = VertexBufferGroup()

        # Create a layout with attribute that has no corresponding VBO
        attr_spec = AttributeSpec(
            name="nonexistent",
            index=0,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=0,
            offset=0,
        )
        layout = LayoutDescriptor(attributes=[attr_spec])
        vbg.layout = layout

        # Should not raise error, just skip missing VBO
        vbg.bind()

    def test_unbind_with_layout(self):
        """Test unbind method with layout."""
        vbg = VertexBufferGroup()

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
        vbg.layout = layout

        vbg.unbind()

        # The unbind method should disable vertex attrib arrays
        # This is already mocked in setUp

    def test_unbind_without_layout(self):
        """Test unbind method without layout."""
        vbg = VertexBufferGroup()

        # Should return early without processing
        vbg.unbind()
        # No assertions needed - should not raise any errors

    def test_delete(self):
        """Test delete method."""
        vbg = VertexBufferGroup()

        # Add some mock buffers
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()
        mock_nbo = MagicMock()
        mock_ebo = MagicMock()

        vbg.vbo = mock_vbo
        vbg.cbo = mock_cbo
        vbg.nbo = mock_nbo
        vbg.ebo = mock_ebo

        # Set up layout
        layout = LayoutDescriptor(attributes=[])
        vbg.layout = layout

        vbg.delete()

        # Verify buffers were deleted
        # The delete_buffer_object calls are mocked in setUp

        # Verify internal state was cleared
        self.assertIsNone(vbg.nbo)
        self.assertIsNone(vbg.cbo)
        self.assertIsNone(vbg.vbo)
        self.assertIsNone(vbg.ebo)
        self.assertIsNone(vbg.layout)

    def test_delete_with_none_buffers(self):
        """Test delete method with None buffers."""
        vbg = VertexBufferGroup()

        # All buffers are None by default
        vbg.delete()

        # Should not raise any errors
        self.assertIsNone(vbg.vbo)
        self.assertIsNone(vbg.cbo)
        self.assertIsNone(vbg.nbo)
        self.assertIsNone(vbg.ebo)

    def test_context_manager(self):
        """Test that VertexBufferGroup can be used as a context manager."""
        vbg = VertexBufferGroup()

        # Test that __enter__ and __exit__ methods exist
        self.assertTrue(hasattr(vbg, "__enter__"))
        self.assertTrue(hasattr(vbg, "__exit__"))

        # Test context manager usage
        with patch.object(vbg, "bind") as mock_bind, patch.object(
            vbg, "unbind"
        ) as mock_unbind:
            with vbg as context_vbg:
                self.assertEqual(context_vbg, vbg)
                mock_bind.assert_called_once()

            mock_unbind.assert_called_once()

    def test_error_handling_in_add_vbo(self):
        """Test error handling in add_vbo method."""
        vbg = VertexBufferGroup()

        # Mock an exception during VBO creation by mocking get_buffer_class
        mock_vbo_class = MagicMock()
        mock_vbo_class.side_effect = Exception("VBO creation error")

        with patch.object(vbg, "get_buffer_class", return_value=mock_vbo_class):
            # The new add_vbo method should let exceptions propagate
            with self.assertRaises(Exception) as context:
                vbg.add_vbo(VBOType.VBO, data=self.test_data)

            # Verify the exception message
            self.assertIn("VBO creation error", str(context.exception))

    def test_error_handling_in_bind(self):
        """Test error handling in bind method."""
        vbg = VertexBufferGroup()

        # Create a layout that will cause an error
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
        vbg.layout = layout

        # Add mock VBO that will cause an error
        mock_vbo = MagicMock()
        mock_vbo.handle = 123
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo

        with patch(
            "picogl.gpu.buffers.vertex.legacy.glVertexPointer",
            side_effect=Exception("OpenGL error"),
        ):
            with patch("picogl.gpu.buffers.vertex.legacy.log.error") as mock_log_error:
                vbg.bind()
                mock_log_error.assert_called_once()
                self.assertIn("error", mock_log_error.call_args[0][0])

    def test_bind_without_ebo(self):
        """bind() skips EBO when geometry uses glDrawArrays only."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()
        mock_vbo.handle = 42
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name=VertexBufferRole.VBO,
                    index=0,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                )
            ]
        )

        with patch("picogl.gpu.buffers.vertex.legacy.glVertexPointer"), patch(
            "picogl.gpu.buffers.vertex.legacy.gl_enableClientState"
        ), patch("picogl.gpu.buffers.vertex.legacy.glBindBuffer") as mock_bind_buffer:
            vbg.bind()
            mock_bind_buffer.assert_called()

    def test_bind_legacy_buffer_roles(self):
        """bind() resolves pointer method names and VertexBufferRole attributes."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()
        mock_vbo.handle = 42
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo

        attr_spec = AttributeSpec(
            name=VertexBufferRole.VBO,
            index=0,
            size=3,
            type=GL_FLOAT,
            normalized=False,
            stride=12,
            offset=0,
        )
        vbg.layout = LayoutDescriptor(attributes=[attr_spec])

        with patch(
            "picogl.gpu.buffers.vertex.legacy.glVertexPointer"
        ) as mock_vertex_pointer, patch(
            "picogl.gpu.buffers.vertex.legacy.gl_enableClientState"
        ) as mock_enable_state:
            vbg.bind()
            mock_enable_state.assert_called_once_with(GL_VERTEX_ARRAY)
            mock_vertex_pointer.assert_called_once()
            args = mock_vertex_pointer.call_args[0]
            self.assertEqual(args[:3], (3, GL_FLOAT, 12))
            self.assertIsInstance(args[3], ctypes.c_void_p)

    def test_bind_uses_vbo_handle(self):
        """bind() passes VBO handle to glBindBuffer, not the buffer object."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()
        mock_vbo.handle = 77
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name=VertexBufferRole.VBO,
                    index=0,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                )
            ]
        )

        with patch("picogl.gpu.buffers.vertex.legacy.glVertexPointer"), patch(
            "picogl.gpu.buffers.vertex.legacy.gl_enableClientState"
        ), patch("picogl.gpu.buffers.vertex.legacy.glBindBuffer") as mock_bind_buffer:
            vbg.bind()
            mock_bind_buffer.assert_any_call(GL_ARRAY_BUFFER, 77)

    def test_bind_resolves_role_from_attr_role(self):
        """bind() uses AttributeSpec.role as the canonical buffer role."""
        vbg = VertexBufferGroup()
        mock_cbo = MagicMock()
        mock_cbo.handle = 55
        vbg.named_vbos[VertexBufferRole.CBO] = mock_cbo
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name="misleading_name",
                    index=2,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                    role=VertexBufferRole.CBO,
                )
            ]
        )

        with patch(
            "picogl.gpu.buffers.vertex.legacy.glColorPointer"
        ) as mock_color_pointer, patch(
            "picogl.gpu.buffers.vertex.legacy.gl_enableClientState"
        ), patch(
            "picogl.gpu.buffers.vertex.legacy.glBindBuffer"
        ):
            vbg.bind()
            mock_color_pointer.assert_called_once()

    def test_bind_resolves_role_from_vbo_type(self):
        """bind() resolves buffer role from AttributeSpec.vbo_type."""
        vbg = VertexBufferGroup()
        mock_cbo = MagicMock()
        mock_cbo.handle = 55
        vbg.named_vbos[VertexBufferRole.CBO] = mock_cbo
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name="colors",
                    index=2,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                    vbo_type=VBOType.CBO,
                    role=VertexBufferRole.CBO,
                )
            ]
        )

        with patch(
            "picogl.gpu.buffers.vertex.legacy.glColorPointer"
        ) as mock_color_pointer, patch(
            "picogl.gpu.buffers.vertex.legacy.gl_enableClientState"
        ), patch(
            "picogl.gpu.buffers.vertex.legacy.glBindBuffer"
        ):
            vbg.bind()
            mock_color_pointer.assert_called_once()

    def test_compat_properties_sync_named_vbos(self):
        """vbo/cbo/nbo/ebo properties read and write named_vbos."""
        vbg = VertexBufferGroup()
        mock_vbo = MagicMock()
        mock_cbo = MagicMock()

        vbg.add_vbo_object(VBOType.VBO, mock_vbo)
        vbg.cbo = mock_cbo

        self.assertIs(vbg.vbo, mock_vbo)
        self.assertIs(vbg.named_vbos[VertexBufferRole.VBO], mock_vbo)
        self.assertIs(vbg.cbo, mock_cbo)
        self.assertIs(vbg.named_vbos[VertexBufferRole.CBO], mock_cbo)

        replacement = MagicMock()
        vbg.vbo = replacement
        self.assertIs(vbg.named_vbos[VertexBufferRole.VBO], replacement)

        vbg.vbo = None
        self.assertIsNone(vbg.vbo)
        self.assertNotIn(VertexBufferRole.VBO, vbg.named_vbos)

    def test_draw_elements_uses_layout_bind_only(self):
        """draw_elements() relies on layout bind(), not per-VBO bind()."""
        vbg = VertexBufferGroup()
        mock_ebo = MagicMock()
        mock_ebo.handle = 99
        vbg.ebo = mock_ebo
        mock_vbo = MagicMock()
        mock_vbo.handle = 42
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name=VertexBufferRole.VBO,
                    index=0,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                )
            ]
        )

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states, patch(
            "picogl.gpu.buffers.vertex.legacy.glDrawElements"
        ):
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw_elements(count=3, mode=GLDrawMode.TRIANGLES)

        mock_vbo.bind.assert_not_called()

    def test_type_conversion_in_bind(self):
        """Test type conversion handling in bind method."""
        vbg = VertexBufferGroup()

        # Create a layout with various type scenarios
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
        vbg.layout = layout

        # Add mock VBO
        mock_vbo = MagicMock()
        mock_vbo.handle = 123
        vbg.named_vbos[VertexBufferRole.VBO] = mock_vbo

        with patch(
            "picogl.gpu.buffers.vertex.legacy.glVertexPointer"
        ) as mock_vertex_pointer:
            vbg.bind()
            mock_vertex_pointer.assert_called_once()

    def test_repr_string(self):
        """Test string representation of VertexBufferGroup."""
        vbg = VertexBufferGroup()
        repr_str = repr(vbg)

        self.assertIn("VertexBufferGroup", repr_str)
        # The default repr doesn't include specific attributes, just test that it's a valid repr
        self.assertTrue(repr_str.startswith("<"))
        self.assertTrue(repr_str.endswith(">"))

    def test_vbo_classes_mapping(self):
        """Test VBO classes mapping is correct."""
        vbg = VertexBufferGroup()

        expected_mappings = {
            VBOType.VBO: "LegacyPositionVBO",
            VBOType.CBO: "LegacyColorVBO",
            VBOType.EBO: "LegacyEBO",
            VBOType.NBO: "LegacyNormalVBO",
        }

        for key, expected_class_name in expected_mappings.items():
            vbo_class = vbg.vbo_classes[key]
            self.assertEqual(vbo_class.__name__, expected_class_name)

    def test_resolve_client_states(self):
        """_resolve_client_states() derives gl client states from layout roles."""
        vbg = VertexBufferGroup()
        vbg.named_vbos[VertexBufferRole.VBO] = MagicMock()
        vbg.named_vbos[VertexBufferRole.CBO] = MagicMock()
        vbg.layout = LayoutDescriptor(
            attributes=[
                AttributeSpec(
                    name=VertexBufferRole.VBO,
                    index=0,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                ),
                AttributeSpec(
                    name=VertexBufferRole.CBO,
                    index=2,
                    size=3,
                    type=GL_FLOAT,
                    normalized=False,
                    stride=0,
                    offset=0,
                ),
            ]
        )

        states = vbg._resolve_client_states()
        self.assertEqual(states, (GL_VERTEX_ARRAY, GL_COLOR_ARRAY))

    def test_legacy_client_states_integration(self):
        """Test integration with legacy client states."""
        vbg = VertexBufferGroup()

        # Add some mock VBOs
        mock_vbo = MagicMock()
        vbg.named_vbos = {VBOType.VBO: mock_vbo}

        with patch(
            "picogl.gpu.buffers.vertex.legacy.legacy_client_states"
        ) as mock_client_states:
            mock_client_states.return_value.__enter__ = MagicMock()
            mock_client_states.return_value.__exit__ = MagicMock()

            vbg.draw()

            # Verify legacy client states were called with correct parameters
            mock_client_states.assert_called_once_with(
                GL_VERTEX_ARRAY, GL_COLOR_ARRAY, GL_NORMAL_ARRAY
            )


if __name__ == "__main__":
    unittest.main()
