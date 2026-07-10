"""
Prepare viewport
"""

import platform


def get_dpr() -> int:
    """get device pixel ratio (viewport)"""
    if platform.system() == "Darwin":
        dpr = 2  # macOS Retina displays
    else:
        dpr = 1
    return dpr
