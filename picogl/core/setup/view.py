from backend.gl.api.clear import gl_clear
from backend.gl.enums import GLBitMask
from backend.gl.enums.legacy.scale import gl_load_identity


def gl_setup_view():
    gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
    gl_load_identity()