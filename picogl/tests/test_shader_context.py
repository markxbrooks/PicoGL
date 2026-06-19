"""Tests for shader GL context guards."""

import unittest
from unittest.mock import patch

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.shaders.manager import ShaderManager


class TestShaderContext(unittest.TestCase):
    @patch(
        "picogl.backend.modern.core.shader.context.gl_context_available",
        return_value=False,
    )
    def test_shader_program_bind_requires_context(self, _avail):
        program = ShaderProgram(shader_name="test")
        program.program = 1
        with self.assertRaises(RuntimeError):
            program.bind()

    @patch(
        "picogl.backend.modern.core.shader.context.gl_context_available",
        return_value=True,
    )
    @patch(
        "picogl.backend.modern.core.shader.context.program_is_valid",
        return_value=False,
    )
    def test_shader_program_bind_rejects_invalid_program(self, _valid, _avail):
        program = ShaderProgram(shader_name="test")
        program.program = 99
        with self.assertRaises(RuntimeError):
            program.bind()

    @patch(
        "picogl.shaders.manager.gl_context_available",
        return_value=False,
    )
    def test_initialize_shaders_defers_without_context(self, _avail):
        manager = ShaderManager()
        manager.initialize_shaders(shader_dir="/tmp")
        self.assertFalse(manager._initialized)
        self.assertEqual(len(manager.shaders), 0)

    @patch(
        "picogl.backend.modern.core.shader.context.gl_context_available",
        return_value=False,
    )
    def test_use_shader_type_returns_false_without_context(self, _avail):
        manager = ShaderManager()
        from picogl.shaders.type import ShaderType

        result = manager.use_shader_type(ShaderType.DEFAULT)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
