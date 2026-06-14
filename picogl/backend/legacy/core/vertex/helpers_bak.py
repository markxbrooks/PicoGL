"""
GL Clear Buffers
"""

from picogl.backend.GL.backend import GLBackend


def gl_clear_buffers(backend: GLBackend) -> None:
    """
    gl_clear_buffers

    Clears the color_array and depth atoms_buffers and resets modelview matrix.
    """
    backend.set_matrix_mode_model_view()
    backend.load_identity()
    backend.set_depth_test()
    backend.enable_multisample()
    backend.clear_color(color=(0.0, 0.0, 0.0, 1.0))
