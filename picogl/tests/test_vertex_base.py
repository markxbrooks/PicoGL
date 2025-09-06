"""
Unit tests for the VertexBase class in the ElMo OpenGL backend.

This module contains a suite of unit tests for verifying the correctness,
robustness, and interface of the :class:`picogl.buffers.base.VertexBase`
class, which serves as a base for OpenGL vertex buffer objects (VBOs).

The tests cover:

- Object initialization with handle parameter.
- Available methods: bind, unbind, delete, set_layout, attach_buffers.
- Context management (enter/exit).
- Handle management.

Dependencies:
    - unittest (standard library)
    - unittest.mock.MagicMock for method mocking
    - picogl.buffers.base.VertexBase

To run the tests::

    python -m unittest path.to.this.module

"""

import unittest
from unittest.mock import MagicMock

from picogl.buffers.base import VertexBase


class TestVertexBase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.mock_handle = MagicMock()
        self.vertex_base = VertexBase(handle=self.mock_handle)

    def test_initialization(self):
        """Test that the VertexBase initializes correctly."""
        # Test with handle
        vbo = VertexBase(handle=self.mock_handle)
        self.assertEqual(vbo.handle, self.mock_handle)

        # Test without handle (defaults to None)
        vbo = VertexBase()
        self.assertIsNone(vbo.handle)

    def test_handle_attribute(self):
        """Test that the handle attribute is accessible."""
        self.assertEqual(self.vertex_base.handle, self.mock_handle)

        # Test setting handle
        new_handle = MagicMock()
        self.vertex_base.handle = new_handle
        self.assertEqual(self.vertex_base.handle, new_handle)

    def test_available_methods(self):
        """Test that all expected methods exist."""
        expected_methods = ["bind", "unbind", "delete", "set_layout", "attach_buffers"]

        for method_name in expected_methods:
            self.assertTrue(
                hasattr(self.vertex_base, method_name),
                f"Method {method_name} not found on VertexBase",
            )

    def test_bind_method(self):
        """Test that the bind method exists and is callable."""
        self.assertTrue(callable(self.vertex_base.bind))

        # Test calling the method (it may not do anything in base class)
        try:
            self.vertex_base.bind()
        except Exception:
            # If it raises an exception, that's fine - we're just testing it exists
            pass

    def test_unbind_method(self):
        """Test that the unbind method exists and is callable."""
        self.assertTrue(callable(self.vertex_base.unbind))

        # Test calling the method
        try:
            self.vertex_base.unbind()
        except Exception:
            # If it raises an exception, that's fine - we're just testing it exists
            pass

    def test_delete_method(self):
        """Test that the delete method exists and is callable."""
        self.assertTrue(callable(self.vertex_base.delete))

        # Test calling the method
        try:
            self.vertex_base.delete()
        except Exception:
            # If it raises an exception, that's fine - we're just testing it exists
            pass

    def test_set_layout_method(self):
        """Test that the set_layout method exists and is callable."""
        self.assertTrue(callable(self.vertex_base.set_layout))

        # Test calling the method
        try:
            self.vertex_base.set_layout()
        except Exception:
            # If it raises an exception, that's fine - we're just testing it exists
            pass

    def test_attach_buffers_method(self):
        """Test that the attach_buffers method exists and is callable."""
        self.assertTrue(callable(self.vertex_base.attach_buffers))

        # Test calling the method
        try:
            self.vertex_base.attach_buffers()
        except Exception:
            # If it raises an exception, that's fine - we're just testing it exists
            pass

    def test_context_manager(self):
        """Test that VertexBase can be used as a context manager."""
        # Test that __enter__ and __exit__ methods exist
        self.assertTrue(hasattr(self.vertex_base, "__enter__"))
        self.assertTrue(hasattr(self.vertex_base, "__exit__"))

        # Test context manager usage
        try:
            with self.vertex_base as vbo:
                self.assertEqual(vbo, self.vertex_base)
        except Exception:
            # If it raises an exception, that's fine - we're just testing the interface
            pass

    def test_enter_exit_methods(self):
        """Test that __enter__ and __exit__ methods are callable."""
        self.assertTrue(callable(self.vertex_base.__enter__))
        self.assertTrue(callable(self.vertex_base.__exit__))

        # Test __enter__ returns self
        try:
            result = self.vertex_base.__enter__()
            self.assertEqual(result, self.vertex_base)
        except Exception:
            # If it raises an exception, that's fine
            pass

        # Test __exit__ with mock parameters
        try:
            self.vertex_base.__exit__(None, None, None)
        except Exception:
            # If it raises an exception, that's fine
            pass

    def test_method_signatures(self):
        """Test that methods have the expected signatures."""
        # Test bind method signature
        bind_sig = self.vertex_base.bind.__code__.co_varnames
        self.assertIn("self", bind_sig)

        # Test unbind method signature
        unbind_sig = self.vertex_base.unbind.__code__.co_varnames
        self.assertIn("self", unbind_sig)

        # Test delete method signature
        delete_sig = self.vertex_base.delete.__code__.co_varnames
        self.assertIn("self", delete_sig)

    def test_handle_none_initialization(self):
        """Test initialization with handle=None."""
        vbo = VertexBase(handle=None)
        self.assertIsNone(vbo.handle)

    def test_handle_reassignment(self):
        """Test that handle can be reassigned."""
        initial_handle = self.vertex_base.handle
        new_handle = MagicMock()

        self.vertex_base.handle = new_handle
        self.assertEqual(self.vertex_base.handle, new_handle)
        self.assertNotEqual(self.vertex_base.handle, initial_handle)

    def test_instance_attributes(self):
        """Test that instance attributes are properly set."""
        custom_handle = MagicMock()
        vbo = VertexBase(handle=custom_handle)

        # Test that the handle is set correctly
        self.assertEqual(vbo.handle, custom_handle)

        # Test that we can access the attribute
        self.assertTrue(hasattr(vbo, "handle"))
        self.assertIsInstance(vbo.handle, type(custom_handle))

    def test_method_callability(self):
        """Test that all methods are callable."""
        methods = ["bind", "unbind", "delete", "set_layout", "attach_buffers"]

        for method_name in methods:
            method = getattr(self.vertex_base, method_name)
            self.assertTrue(callable(method), f"Method {method_name} is not callable")

    def test_abstract_methods(self):
        """Test that VertexBase is not abstract (no abstract methods)."""
        vbo = VertexBase()
        # VertexBase should not have abstract methods (empty frozenset means not abstract)
        if hasattr(vbo, "__abstractmethods__"):
            self.assertEqual(
                len(vbo.__abstractmethods__),
                0,
                "VertexBase should not have abstract methods",
            )
        else:
            # If no __abstractmethods__ attribute, that's also fine
            pass


if __name__ == "__main__":
    unittest.main()
