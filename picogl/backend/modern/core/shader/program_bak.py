"""
This module provides a ShaderProgram class for managing OpenGL shader programs.
It includes functionality for initializing shaders from GLSL files or source code,
compiling and linking shaders, and setting uniform values.

"""
from pathlib import Path

import numpy as np
from backend.gl.enums.shader import GLShader
from decologr import Decologr as log
from picogl.backend.gl.wrappers.shader import (gl_create_program,
                                               gl_get_program_info_log,
                                               gl_get_programiv,
                                               gl_link_program, gl_use_program)
from picogl.backend.modern.core.shader.compile import compile_shader
from picogl.backend.modern.core.shader.context import (clear_gl_errors,
                                                       gl_context_available,
                                                       program_is_valid,
                                                       require_gl_context)
from picogl.backend.modern.core.shader.helpers import (log_gl_error,
                                                       read_shader_source)
from picogl.backend.modern.core.uniform.location_value import \
    set_uniform_location_value
from picogl.boolean import GLBoolean
from picogl.shaders.uniform import get_uniform_location


class ShaderProgram:
    """OpenGL Shader program manager for vertex and fragment shaders."""

    def __init__(
        self,
        shader_name: str = None,
        vertex_source_file: str = None,
        fragment_source_file: str = None,
        glsl_dir: str | Path | None = None,
    ):
        """constructor"""
        self.shader_name = shader_name
        self.vertex_source_file = vertex_source_file
        self.fragment_source_file = fragment_source_file
        self.base_dir = glsl_dir
        self.vertex_shader = None
        self.fragment_shader = None
        self.program = None
        self.uniforms = {}
        self._uniform_state = {}

        if vertex_source_file is not None and vertex_source_file is not None:
            self.init_shader_from_glsl_files(
                vertex_source_file=vertex_source_file,
                fragment_source_file=fragment_source_file,
                glsl_dir=glsl_dir,
            )

    def __str__(self):
        return f"PicoGLShader(name={self.shader_name}, program={self.program})"

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    def program_id(self):
        return self.program

    def init_shader_from_glsl_files(
        self,
        vertex_source_file: str,
        fragment_source_file: str,
        glsl_dir: str | Path | None = None,
    ) -> None:
        """
        init_shader_from_glsl_files

        :param glsl_dir: directory containing vertex shaders
        :param vertex_source_file: list of paths to vertex shaders
        :param fragment_source_file: list of paths to fragment shaders
        :return: None
        """
        vertex_sources = read_shader_source(vertex_source_file, glsl_dir=glsl_dir)
        fragment_sources = read_shader_source(fragment_source_file, glsl_dir=glsl_dir)
        self.init_shader_from_glsl(vertex_sources, fragment_sources)

    def init_shader_from_glsl(self, vertex_source: str, fragment_source: str) -> None:
        """
        init_shader_from_glsl

        :param vertex_source: list of paths to vertex shaders
        :param fragment_source: list of paths to fragment shaders
        :return: None
        """
        self.init_shader(vertex_source, fragment_source)

    def init_shader(self, vertex_source: str, fragment_source: str):
        """
        init_shader

        :param vertex_source: list of paths to vertex shaders
        :param fragment_source: list of paths to fragment shaders
        :return: None

        Create, compile, and link shaders into a program.
        """
        self.create_shader_program()
        log.parameter("self.program", self.program, silent=True)
        log.parameter("vertex_source", vertex_source, silent=True)
        log.parameter("fragment_source", fragment_source, silent=True)
        self.vertex_shader = compile_shader(
            self.program, GLShader.VERTEX_SHADER, vertex_source
        )
        self.fragment_shader = compile_shader(
            self.program, GLShader.FRAGMENT_SHADER, fragment_source
        )
        self.link_shader_program()

    def create_shader_program(self):
        """
        create_shader_program
        """
        self.program = gl_create_program()
        log.message(f"Created shader program {self.program}", silent=True)
        log_gl_error()

    def link_shader_program(self):
        """
        link_shader_program
        """
        log.message("Linking shader program...", silent=True)
        gl_link_program(self.program)
        if GLBoolean.TRUE != gl_get_programiv(self.program):
            err = gl_get_program_info_log(self.program)
            raise RuntimeError(f"Shader link failed: {err}")
        log_gl_error()

    def uniform(self, name: str, value):
        if name in self._uniform_state:
            if np.array_equal(self._uniform_state[name], value):
                return self  # skip redundant upload

        loc = self.get_uniform_location(name)

        if loc == -1:
            return self

        set_uniform_location_value(loc, value)
        self._uniform_state[name] = value
        return self

    def get_uniform_location(self, uniform_name: str) -> int:
        if uniform_name in self.uniforms:
            return self.uniforms[uniform_name]

        loc = get_uniform_location(
            shader_program=self.program, uniform_name=uniform_name
        )

        self.uniforms[uniform_name] = loc
        return loc

    def begin(self):
        """begin"""
        gl_use_program(self.program)
        log_gl_error()

    def end(self):
        """end"""
        gl_use_program(0)

    def bind(self):
        """Bind this program for uniform uploads and draws."""
        require_gl_context("ShaderProgram.bind")
        if self.program is None:
            raise RuntimeError(f"ShaderProgram {self.shader_name!r} has no GL program")
        clear_gl_errors()
        if not program_is_valid(self.program):
            raise RuntimeError(
                f"ShaderProgram {self.shader_name!r}: program id {self.program} "
                "is not valid in the current OpenGL context"
            )
        gl_use_program(self.program)
        log_gl_error()

    def unbind(self):
        if not gl_context_available():
            return
        clear_gl_errors()
        gl_use_program(0)

    def release(self):
        gl_use_program(0)

    def delete(self):
        self.release()