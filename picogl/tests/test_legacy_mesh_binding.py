"""Tests for LegacyClientMeshBinding and LegacyMesh sticky bind."""

import unittest
from unittest.mock import MagicMock, patch

from picogl.backend.geometry.legacy_mesh import LegacyMesh
from picogl.backend.geometry.legacy_mesh_binding import LegacyClientMeshBinding
from picogl.renderer.initializable import Bindable


class TestLegacyClientMeshBinding(unittest.TestCase):
    def test_is_bindable(self):
        mesh = MagicMock(vertices=None, normals=None, colors=None, texcoords=None)
        binding = LegacyClientMeshBinding(mesh)
        self.assertIsInstance(binding, Bindable)

    @patch("picogl.backend.geometry.legacy_mesh_binding.glEnableClientState")
    @patch("picogl.backend.geometry.legacy_mesh_binding.glVertexPointer")
    def test_bind_enables_vertex_state_once(self, vertex_pointer, enable_state):
        vertices = object()
        mesh = MagicMock(vertices=vertices, normals=None, colors=None, texcoords=None)
        binding = LegacyClientMeshBinding(mesh)

        binding.bind()
        binding.bind()

        enable_state.assert_called_once()
        vertex_pointer.assert_called_once()

    @patch("picogl.backend.geometry.legacy_mesh_binding.glEnableClientState")
    @patch("picogl.backend.geometry.legacy_mesh_binding.glVertexPointer")
    @patch("picogl.backend.geometry.legacy_mesh_binding.glDisableClientState")
    def test_unbind_disables_vertex_state(
        self, disable_state, vertex_pointer, enable_state
    ):
        vertices = object()
        mesh = MagicMock(vertices=vertices, normals=None, colors=None, texcoords=None)
        binding = LegacyClientMeshBinding(mesh)

        binding.bind()
        binding.unbind()

        disable_state.assert_called_once()


class TestLegacyMeshDelegation(unittest.TestCase):
    @patch("picogl.backend.geometry.legacy_mesh_binding.glEnableClientState")
    @patch("picogl.backend.geometry.legacy_mesh_binding.glVertexPointer")
    def test_legacy_mesh_bind_is_sticky(self, vertex_pointer, enable_state):
        mesh = MagicMock(vertices=object(), normals=None, colors=None, texcoords=None)
        legacy = LegacyMesh(mesh)

        legacy.bind()
        legacy.bind()

        enable_state.assert_called_once()
        vertex_pointer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
