"""Tests for shader gl context guards and refactored ShaderManager binding."""

import unittest
from unittest.mock import MagicMock, patch

from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.shaders.manager import ShaderManager
from picogl.shaders.type import ShaderType


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
        result = manager.use_shader_type(ShaderType.DEFAULT)
        self.assertFalse(result)

    @patch("picogl.shaders.manager.gl_context_available", return_value=True)
    def test_initialize_shaders_does_not_recurse_when_bind_fails(self, _avail):
        manager = ShaderManager()

        def _fake_load(shader_type, shader_number=0):
            manager.shaders[shader_type] = ShaderProgram(shader_name=shader_type.value)

        with patch.object(manager, "load_shader", side_effect=_fake_load):
            with patch.object(
                ShaderProgram,
                "bind",
                side_effect=RuntimeError("bind failed"),
            ):
                manager.initialize_shaders(shader_dir="/tmp")

        self.assertFalse(manager._initialized)

    def test_bind_does_not_warm_up_shaders(self):
        manager = ShaderManager()
        program = ShaderProgram(shader_name="atoms")
        program.program = 1
        with patch.object(manager, "initialize_shaders") as init_mock:
            with patch.object(ShaderProgram, "bind"):
                manager.bind(program)
                init_mock.assert_not_called()
        self.assertIs(manager.current_shader, program)
        self.assertEqual(manager.current_shader_program, 1)

    def test_current_shader_program_property_tracks_bound_shader(self):
        manager = ShaderManager()
        program = ShaderProgram(shader_name="bonds")
        program.program = 42
        with patch.object(ShaderProgram, "bind"):
            manager.bind(program)
        self.assertEqual(manager.current_shader_program, 42)
        manager.unbind()
        self.assertIsNone(manager.current_shader_program)

    def test_failed_shader_not_stored_in_shaders_dict(self):
        manager = ShaderManager()
        manager.shader_directory = "/tmp"
        manager._failed.add(ShaderType.BONDS)
        self.assertNotIn(ShaderType.BONDS, manager.shaders)
        self.assertTrue(manager.used_fallback_for(ShaderType.BONDS))


if __name__ == "__main__":
    unittest.main()
