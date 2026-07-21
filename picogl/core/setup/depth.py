from picogl.backend.gl.api.enable import gl_enable
from picogl.backend.gl.capability import GLPipelineCapability


def gl_setup_depth_test():
    gl_enable(GLPipelineCapability.DEPTH_TEST)
