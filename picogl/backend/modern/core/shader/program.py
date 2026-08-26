"""
This module provides a ShaderProgram class for managing OpenGL shader programs.
It includes functionality for initializing shaders from GLSL files or source code,
compiling and linking shaders, and setting uniform values.

"""

from pathlib import Path
from typing import Union, Any

import numpy as np
from pyglm import glm

from decologr import Decologr as log
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_LINK_STATUS

from picogl.backend.gl.api.shader import (GLShader, gl_get_program_info_log,
                                          gl_link_program, gl_use_program)
from picogl.backend.gl.api.shader.create import gl_create_program
from picogl.backend.gl.api.shader.getter import gl_get_program_iv, gl_get_uniform_location
from picogl.backend.modern.core.shader.compile import compile_shader
from picogl.backend.modern.core.shader.context import (clear_gl_errors,
                                                       gl_context_available,
                                                       program_is_valid,
                                                       require_gl_context)
from picogl.backend.modern.core.shader.files import ShaderFiles
from picogl.backend.modern.core.shader.helpers import (log_gl_error,
                                                       read_shader_source)
from picogl.backend.modern.core.uniform.location_value import \
    set_uniform_location_value
from picogl.boolean import GLBoolean


class ShaderCompiler:
    """OpenGL Shader program manager for vertex and fragment shaders."""

    def __init__(self):
        """constructor"""

    def __str__(self):
        return f"ShaderCompiler(name={self.shader_name}, program={self.program})"

    @staticmethod
    def compile_shader_files(
        shader_files: ShaderFiles | None,
    ) -> int:
        """
        init_shader_from_shader_files

        :param shader_files: directory containing vertex shaders
        :return: None
        """
        if shader_files is None:
            raise RuntimeError(f"shader_files object not available")
        if shader_files.vertex is None or shader_files.fragment is None:
            raise FileNotFoundError(
                f"{shader_files.vertex} or {shader_files.fragment} not found"
            )
        # ShaderFiles already joins glsl_dir onto vertex/fragment.
        vertex_sources = read_shader_source(shader_files.vertex)
        fragment_sources = read_shader_source(shader_files.fragment)
        return ShaderCompiler.init_shader(vertex_sources, fragment_sources)

    @staticmethod
    def compile_glsl_files(
        vertex_source_file: str | None,
        fragment_source_file: str | None,
        glsl_dir: str | Path | None = None,
    ) -> int:
        """
        init_shader_from_glsl_files

        :param glsl_dir: directory containing vertex shaders
        :param vertex_source_file: list of paths to vertex shaders
        :param fragment_source_file: list of paths to fragment shaders
        :return: None
        """
        if vertex_source_file is None or fragment_source_file is None:
            raise FileNotFoundError(
                f"{vertex_source_file} or {fragment_source_file} not found"
            )
        vertex_sources = read_shader_source(vertex_source_file, glsl_dir=glsl_dir)
        fragment_sources = read_shader_source(fragment_source_file, glsl_dir=glsl_dir)
        return ShaderCompiler.init_shader(vertex_sources, fragment_sources)

    @staticmethod
    def init_shader(vertex_source: str, fragment_source: str) -> int:
        """
        init_shader

        :param vertex_source: GLSL vertex shader source
        :param fragment_source: GLSL fragment shader source
        :return: Linked OpenGL program id
        """
        program = ShaderCompiler.create_shader_program()
        log.parameter("self.program", program, silent=True)
        log.parameter("vertex_source", vertex_source, silent=True)
        log.parameter("fragment_source", fragment_source, silent=True)
        compile_shader(program, GLShader.VERTEX_SHADER, vertex_source)
        compile_shader(program, GLShader.FRAGMENT_SHADER, fragment_source)
        return ShaderCompiler.link_shader_program(program)

    @staticmethod
    def create_shader_program() -> int:
        """
        create_shader_program
        """
        program = gl_create_program()
        log.message(f"Created shader program {program}", silent=True)
        log_gl_error()
        return program

    @staticmethod
    def link_shader_program(program) -> int:
        """
        link_shader_program
        """
        log.message("Linking shader program...", silent=True)
        gl_link_program(program)
        if GLBoolean.TRUE != gl_get_program_iv(program=program, pname=GL_LINK_STATUS):
            err = gl_get_program_info_log(program)
            raise RuntimeError(f"Shader link failed: {err}")
        log_gl_error()
        return program


class ShaderProgram:
    """OpenGL Shader program manager for vertex and fragment shaders."""

    def __init__(
        self,
        shader_name: str = None,
        vertex_source_file: str | Path = None,
        fragment_source_file: str | Path = None,
        glsl_dir: str | Path = None,
    ):
        """constructor"""
        self.shader_name = shader_name
        self.vertex_source_file = vertex_source_file
        self.fragment_source_file = fragment_source_file
        self.base_dir = glsl_dir
        self.vertex_shader = None
        self.fragment_shader = None
        self._program: int | None = None
        self.uniforms = {}
        self._uniform_state = {}
        self.compiler = ShaderCompiler()

        if (
            vertex_source_file is not None
            and fragment_source_file is not None
            and glsl_dir is not None
        ):
            self._program = self.compiler.compile_shader_files(
                ShaderFiles(
                    vertex=vertex_source_file,
                    fragment=fragment_source_file,
                    glsl_dir=glsl_dir,
                )
            )

    def __str__(self):
        return f"ShaderProgram(name={self.shader_name}, program={self.program})"

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()

    @property
    def program(self):
        return self._program

    @program.setter
    def program(self, value):
        self._program = value

    def init_shader_from_shader_files(
        self,
        shader_files: ShaderFiles | None,
    ) -> None:
        """
        init_shader_from_shader_files

        :param shader_files: directory containing vertex shaders
        :return: None
        """
        if shader_files is None:
            raise RuntimeError(f"shader_files object not available")
        if shader_files.vertex is None or shader_files.fragment is None:
            raise FileNotFoundError(
                f"{shader_files.vertex} or {shader_files.fragment} not found"
            )
        # ShaderFiles already joins glsl_dir onto vertex/fragment.
        vertex_sources = read_shader_source(shader_files.vertex)
        fragment_sources = read_shader_source(shader_files.fragment)
        self.init_shader_from_glsl(vertex_sources, fragment_sources)

    def init_shader_from_glsl_files(
        self,
        vertex_source_file: str | None,
        fragment_source_file: str | None,
        glsl_dir: str | Path | None = None,
    ) -> None:
        """
        init_shader_from_glsl_files

        :param glsl_dir: directory containing vertex shaders
        :param vertex_source_file: list of paths to vertex shaders
        :param fragment_source_file: list of paths to fragment shaders
        :return: None
        """
        if vertex_source_file is None or fragment_source_file is None:
            raise FileNotFoundError(
                f"{vertex_source_file} or {fragment_source_file} not found"
            )
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
        if GLBoolean.TRUE != gl_get_program_iv(
            program=self.program, pname=GL_LINK_STATUS
        ):
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

    def set_uniform_name_value(
            self,
            uniform_name: str,
            uniform_value: Union[
                float, int, glm.vec2, glm.vec3, glm.vec4, glm.mat4, np.ndarray
            ],
    ):
        """
        set_uniform_name_value

        :param uniform_name: Name of the uniform variable
        :param uniform_value: Value to set (supports float, int, vec2, vec3, vec4, mat4, or np.ndarray)

        Set a uniform variable in a shader program
        """
        location = self.get_uniform_location(uniform_name)
        if location == -1 or location is None:
            log.warning(f"Uniform '{uniform_name}' not found in shader {self.name}.")
            return
        set_uniform_location_value(location, uniform_value)

    def get_location_for_uniform_name(self, uniform_name: str) -> Any:
        location = gl_get_uniform_location(self.program, uniform_name)
        return location

    def get_uniform_location(self, uniform_name: str) -> Any | None:
        if uniform_name in self.uniforms:
            return self.uniforms[uniform_name]
        if self.program is None:
            return None
        loc = gl_get_uniform_location(
            program=self.program, name=uniform_name
        )

        self.set_uniform_location_name(loc, uniform_name)
        return loc

    def set_uniform_location_name(self, loc: Any | None, uniform_name: str):
        self.uniforms[uniform_name] = loc

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
