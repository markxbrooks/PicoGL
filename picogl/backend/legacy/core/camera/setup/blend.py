"""
Enable blending
"""


def enable_blending(backend: "GLBackend") -> None:
    """
    enable_blending

    :param backend: Backend to use
    :return: None
    """
    backend.blend.set_blend(True)
    backend.blend.setup_blending()
    black = (0.0, 0.0, 0.0, 1.0)
    backend.frame.set_clear_color(black)
