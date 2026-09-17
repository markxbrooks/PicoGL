"""
Enable blending
"""

from picogl.core.rgbcolor import RGBATuple


def enable_blending(backend: "GLBackend") -> None:
    """
    enable_blending

    :param backend: Backend to use
    :return: None
    """
    backend.blend.set_blend(True)
    backend.blend.set_alpha_blending()
    backend.frame.set_clear_color(RGBATuple.BLACK)
