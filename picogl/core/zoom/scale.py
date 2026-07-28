from picogl.backend.gl.enums.legacy.scale import gl_scalef


def gl_scale_by_zoom(zoom: float):
    gl_scalef(zoom, zoom, zoom)