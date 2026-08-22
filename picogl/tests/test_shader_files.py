"""Tests for ShaderFiles path joining and shader source reads."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from picogl.backend.modern.core.shader.files import ShaderFiles
from picogl.backend.modern.core.shader.helpers import read_shader_source
from picogl.backend.modern.core.shader.program import ShaderCompiler


class TestShaderFiles(unittest.TestCase):
    def test_shader_files_joins_dir_once(self):
        files = ShaderFiles(
            vertex="vertex.glsl",
            fragment="fragment.glsl",
            glsl_dir="glsl/tu02",
        )
        self.assertEqual(files.vertex, Path("glsl/tu02/vertex.glsl"))
        self.assertEqual(files.fragment, Path("glsl/tu02/fragment.glsl"))

    def test_read_shader_source_does_not_rejoin_shader_files_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            glsl_dir = Path(tmp) / "glsl" / "tu02"
            glsl_dir.mkdir(parents=True)
            shader = glsl_dir / "vertex.glsl"
            shader.write_text("void main() {}\n")
            files = ShaderFiles(
                vertex="vertex.glsl",
                fragment="fragment.glsl",
                glsl_dir=glsl_dir,
            )
            source = read_shader_source(files.vertex, glsl_dir=files.glsl_dir)
            self.assertEqual(source, "void main() {}\n")

    def test_read_shader_source_joins_bare_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            glsl_dir = Path(tmp)
            shader = glsl_dir / "fragment.glsl"
            shader.write_text("precision mediump float;\n")
            source = read_shader_source("fragment.glsl", glsl_dir=glsl_dir)
            self.assertEqual(source, "precision mediump float;\n")


class TestShaderCompiler(unittest.TestCase):
    @patch("picogl.backend.modern.core.shader.program.compile_shader")
    @patch(
        "picogl.backend.modern.core.shader.program.ShaderCompiler.link_shader_program",
        return_value=7,
    )
    @patch(
        "picogl.backend.modern.core.shader.program.ShaderCompiler.create_shader_program",
        return_value=7,
    )
    def test_init_shader_callable_without_instance(self, create, link, compile_shader):
        program = ShaderCompiler.init_shader("void main() {}", "void main() {}")
        self.assertEqual(program, 7)
        create.assert_called_once()
        link.assert_called_once_with(7)
        self.assertEqual(compile_shader.call_count, 2)


if __name__ == "__main__":
    unittest.main()
