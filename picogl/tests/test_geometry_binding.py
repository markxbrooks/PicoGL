"""Tests for GPUMesh upload factory and geometry driver integration."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_TRIANGLES

from picogl.backend.geometry.adapter import DrawableBufferAdapter
from picogl.backend.geometry.factory import LegacyBinding, ModernBinding
from picogl.backend.geometry.legacy_mesh import LegacyMesh
from picogl.backend.geometry.modern_mesh import ModernMesh
from picogl.backend.gl.driver.geometry import GLGeometryDriver
from picogl.renderer.meshdata import MeshData


class TestLegacyMesh(unittest.TestCase):
    def test_upload_returns_legacy_mesh(self):
        mesh = MeshData(
            vertices=np.zeros((3, 3), dtype=np.float32),
            indices=np.array([0, 1, 2], dtype=np.uint32),
        )
        gpu = LegacyBinding().upload(mesh)
        self.assertIsInstance(gpu, LegacyMesh)
        self.assertIs(gpu.mesh, mesh)

    def test_bind_enables_vertex_array(self):
        mesh = SimpleNamespace(
            vertices=object(),
            normals=None,
            colors=None,
            texcoords=None,
            indices=None,
        )
        gpu = LegacyMesh(mesh)

        with (
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_enable_legacy_client_state"
            ) as enable,
            patch(
                "picogl.backend.geometry.legacy_mesh_binding.gl_vertex_array_pointer"
            ),
        ):
            gpu.bind()

        self.assertTrue(enable.called)


class TestModernMesh(unittest.TestCase):
    def test_wraps_gl_mesh(self):
        gl_mesh = MagicMock()
        gl_mesh.vao = object()
        gl_mesh.index_count = 12
        gpu = ModernMesh(gl_mesh=gl_mesh)

        gpu.bind()
        gl_mesh.upload.assert_called_once()
        gl_mesh.bind.assert_called_once()

        gpu.draw(GL_TRIANGLES)
        gl_mesh.draw.assert_called_once_with(mode=GL_TRIANGLES)

        gpu.delete()
        gl_mesh.delete.assert_called_once()


class TestModernBindingUpload(unittest.TestCase):
    def test_upload_gpu_object_wraps_ebo_mesh(self):
        mesh = SimpleNamespace(ebo=1, index_count=3)
        gpu = ModernBinding().upload_gpu_object(mesh)

        self.assertIsInstance(gpu, ModernMesh)
        self.assertEqual(gpu._index_count, 3)


class TestDrawableBufferAdapter(unittest.TestCase):
    def test_delegates_bind_draw_delete(self):
        buffer = MagicMock()
        adapter = DrawableBufferAdapter(buffer, draw_kwargs={"index_count": 4})

        adapter.bind()
        buffer.bind.assert_called_once()

        adapter.draw(GL_TRIANGLES)
        buffer.draw.assert_called_once_with(mode=GL_TRIANGLES, index_count=4)

        adapter.unbind()
        buffer.unbind.assert_called_once()

        adapter.delete()
        buffer.delete.assert_called_once()


class TestGLGeometryDriver(unittest.TestCase):
    def test_draw_gpu_mesh_binds_draws_and_unbinds(self):
        gpu_mesh = MagicMock()
        driver = GLGeometryDriver(binding=LegacyBinding())

        driver.draw_gpu_mesh(gpu_mesh, GL_TRIANGLES)

        gpu_mesh.bind.assert_called_once()
        gpu_mesh.draw.assert_called_once_with(GL_TRIANGLES)
        gpu_mesh.unbind.assert_called_once()

    def test_draw_mesh_uses_binding_shim(self):
        binding = MagicMock()
        driver = GLGeometryDriver(binding=binding)
        mesh = object()

        driver.draw_mesh(mesh, GL_TRIANGLES)

        binding.bind_mesh.assert_called_once_with(mesh)
        binding.draw.assert_called_once_with(mesh, GL_TRIANGLES)


if __name__ == "__main__":
    unittest.main()
