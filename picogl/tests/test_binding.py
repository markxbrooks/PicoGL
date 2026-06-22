"""Tests for gl binding strategies."""

import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

from OpenGL.raw.GL.VERSION.GL_1_1 import GL_TRIANGLES
from picogl.backend.geometry.factory import LegacyBinding, ModernBinding
from picogl.backend.geometry.legacy_mesh import LegacyMesh
from picogl.core.enums.numerical import GLNumeric
from picogl.state.client import GLClientState


class TestLegacyBinding(unittest.TestCase):
    def test_bind_mesh_enables_texcoord_array_not_color(self):
        binding = LegacyBinding()
        mesh = SimpleNamespace(
            vertices=object(),
            normals=None,
            colors=None,
            texcoords=object(),
            indices=None,
        )

        with (
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_enable_legacy_client_state"
            ) as enable,
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_vertex_array_pointer"
            ),
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_texcoord_array_pointer"
            ) as texcoord_pointer,
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_color_array_pointer"
            ) as color_pointer,
        ):
            binding.bind_mesh(mesh)

        enable.assert_has_calls(
            [
                call(GLClientState.VERTEX),
                call(GLClientState.TEXCOORD),
            ]
        )
        texcoord_pointer.assert_called_once_with(pointer=mesh.texcoords)
        color_pointer.assert_not_called()

    def test_bind_mesh_enables_all_client_arrays_when_present(self):
        binding = LegacyBinding()
        mesh = SimpleNamespace(
            vertices=object(),
            normals=object(),
            colors=object(),
            texcoords=object(),
            indices=[0, 1, 2],
        )

        with (
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_enable_legacy_client_state"
            ) as enable,
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_vertex_array_pointer"
            ),
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_normal_array_pointer"
            ),
            patch("picogl.backend.geometry.legacy_mesh_binding.gl_color_array_pointer"),
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_texcoord_array_pointer"
            ),
        ):
            binding.bind_mesh(mesh)

        self.assertEqual(
            [c.args[0] for c in enable.call_args_list],
            [
                GLClientState.VERTEX,
                GLClientState.NORMAL,
                GLClientState.COLOR,
                GLClientState.TEXCOORD,
            ],
        )

    def test_draw_issues_indexed_draw_when_indices_present(self):
        binding = LegacyBinding()
        mesh = SimpleNamespace(indices=[0, 1, 2])
        binding._last_gpu_mesh = LegacyMesh(mesh)

        with patch(
            "picogl.backend.geometry.legacy_mesh.gl_draw_elements"
        ) as draw_elements:
            binding.draw(mesh, GL_TRIANGLES)

        draw_elements.assert_called_once_with(
            3, GLNumeric.UNSIGNED_INT, GL_TRIANGLES, pointer=mesh.indices
        )


class TestModernBinding(unittest.TestCase):
    def test_draw_uses_index_count_from_mesh(self):
        binding = ModernBinding()
        mesh = SimpleNamespace(ebo=42, index_count=9)

        with patch(
            "picogl.backend.geometry.modern_mesh.gl_draw_elements"
        ) as draw_elements:
            binding.bind_mesh(mesh)
            binding.draw(mesh, GL_TRIANGLES)

        draw_elements.assert_called_once_with(
            9, GLNumeric.UNSIGNED_INT, GL_TRIANGLES, pointer=None
        )


if __name__ == "__main__":
    unittest.main()
