from picogl.state.client import GLClientState
from picogl.state.draw_mode import GLDataType
from picogl.wrappers.client_state import (
    gl_disable_legacy_client_state,
    gl_enable_legacy_client_state,
)
from picogl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_normal_array_pointer,
    gl_texcoord_array_pointer,
    gl_vertex_array_pointer,
)


class LegacyAttributeBinder:
    """Legacy client-state and vertex attribute pointer operations."""

    @staticmethod
    def enable_vertex_array():
        gl_enable_legacy_client_state(GLClientState.VERTEX)

    @staticmethod
    def disable_vertex_array():
        gl_disable_legacy_client_state(GLClientState.VERTEX)

    @staticmethod
    def set_vertex_pointer(data):
        gl_vertex_array_pointer(pointer=data, size=3, num_type=GLDataType.FLOAT)

    @staticmethod
    def enable_normal_array():
        gl_enable_legacy_client_state(GLClientState.NORMAL)

    @staticmethod
    def disable_normal_array():
        gl_disable_legacy_client_state(GLClientState.NORMAL)

    @staticmethod
    def set_normal_pointer(data):
        gl_normal_array_pointer(pointer=data, num_type=GLDataType.FLOAT)

    @staticmethod
    def enable_color_array():
        gl_enable_legacy_client_state(GLClientState.COLOR)

    @staticmethod
    def disable_color_array():
        gl_disable_legacy_client_state(GLClientState.COLOR)

    @staticmethod
    def set_color_pointer(data, size):
        gl_color_array_pointer(pointer=data, size=size, num_type=GLDataType.FLOAT)

    @staticmethod
    def enable_texcoord_array():
        gl_enable_legacy_client_state(GLClientState.TEXCOORD)

    @staticmethod
    def disable_texcoord_array():
        gl_disable_legacy_client_state(GLClientState.TEXCOORD)

    @staticmethod
    def set_texcoord_pointer(data):
        gl_texcoord_array_pointer(pointer=data, size=2, num_type=GLDataType.FLOAT)
