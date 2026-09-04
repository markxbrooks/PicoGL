from .attach import gl_attach_shader
from .compile import gl_compile_shader
from .create import gl_create_shader
from .getter import (
    gl_get_program_info_log,
    gl_get_programiv,
    gl_get_shader_info_log,
    gl_get_shader_iv,
    gl_get_uniform_location,
)
from .link import gl_link_program
from .source import gl_shader_source
from .uniform import GLShader, gl_uniform_matrix_4fv, gl_uniform_name_matrix_4f
from .use import gl_use_program
