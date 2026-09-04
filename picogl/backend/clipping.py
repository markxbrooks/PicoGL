from contextlib import contextmanager

from picogl.backend.gl.api.enable import (gl_disable_capability_list,
                                          gl_enable_capability_list)
from picogl.backend.gl.enums.legacy import GLLegacyClipPlane


@contextmanager
def gl_clipping_planes(enabled: bool):
    """
    Context manager to enable/disable clipping planes safely.
    Enables clipping planes when True, otherwise disables them.
    Restores previous state at exit if you decide to extend it later.
    """
    try:
        if enabled:
            gl_enable_capability_list(
                [GLLegacyClipPlane.CLIP_PLANE0, GLLegacyClipPlane.CLIP_PLANE1]
            )
        else:
            gl_disable_capability_list(
                [GLLegacyClipPlane.CLIP_PLANE0, GLLegacyClipPlane.CLIP_PLANE1]
            )
        yield
    finally:
        gl_disable_capability_list(
            [GLLegacyClipPlane.CLIP_PLANE0, GLLegacyClipPlane.CLIP_PLANE1]
        )
