"""
Enable blending
"""


def enable_blending(backend: "GLBackend") -> None:
    """
    enable_blending

    :param backend: Backend to use
    :return: None
    """
    backend.set_blend(True)
    backend.setup_blending_funcs()
    black = (0.0, 0.0, 0.0, 1.0)
    backend.set_clear_color(black)
