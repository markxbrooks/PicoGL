"""Tests for split legacy and shader pipelines."""

import unittest
import warnings
from unittest.mock import MagicMock, patch

from picogl.backend.GL.backend import GLBackend
from picogl.backend.geometry.factory import LegacyBinding
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline, LegacyPipeline
from picogl.backend.modern.core.pipeline import ShaderPipeline


class TestShaderPipeline(unittest.TestCase):
    def test_bind_calls_program_bind(self):
        program = MagicMock()
        pipeline = ShaderPipeline(program)

        pipeline.bind()

        program.bind.assert_called_once()

    def test_unbind_calls_gl_use_program_zero(self):
        with patch("picogl.backend.modern.core.pipeline.shader_pipeline.glUseProgram") as use:
            ShaderPipeline(MagicMock()).unbind()

        use.assert_called_once_with(0)

    def test_set_uniforms_delegates_to_program(self):
        program = MagicMock()
        pipeline = ShaderPipeline(program)

        pipeline.set_uniforms({"uMVP": object(), "uAlpha": 0.5})

        self.assertEqual(program.uniform.call_count, 2)

    def test_bind_without_program_raises(self):
        with self.assertRaises(RuntimeError):
            ShaderPipeline().bind()


class TestGLBackendPipelines(unittest.TestCase):
    def test_legacy_is_legacy_pipeline_instance(self):
        backend = GLBackend(binding=LegacyBinding())
        self.assertIsInstance(backend.legacy, GLLegacyPipeline)
        self.assertIsInstance(backend.legacy, LegacyPipeline)

    def test_shader_pipeline_defaults_empty(self):
        backend = GLBackend(binding=LegacyBinding())
        self.assertIsInstance(backend.shader, ShaderPipeline)
        self.assertIsNone(backend.shader.program)

    def test_create_shader_pipeline_sets_backend_shader(self):
        backend = GLBackend(binding=LegacyBinding())
        program = MagicMock()
        pipeline = backend.create_shader_pipeline(program)

        self.assertIs(backend.shader, pipeline)
        self.assertIs(pipeline.program, program)

    def test_pipeline_property_is_deprecated_alias_for_legacy(self):
        backend = GLBackend(binding=LegacyBinding())

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            pipeline = backend.pipeline

        self.assertIs(pipeline, backend.legacy)
        self.assertTrue(any("deprecated" in str(w.message).lower() for w in caught))


if __name__ == "__main__":
    unittest.main()
