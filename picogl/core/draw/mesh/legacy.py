"""
draw legacy mesh
"""
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.backend.gl.api.enable import gl_enable, gl_disable
from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace)
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.state.fill import GLFillMode


def draw_legacy_mesh(mesh: LegacyGLMesh, wireframe_mode):
    """draw legacy mesh"""
    if wireframe_mode:
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        gl_disable(GLFixedFunctionCapability.LIGHTING)
    else:
        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
        gl_enable(GLFixedFunctionCapability.LIGHTING)

    mesh.draw()

    # Reset polygon mode
    gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
    GLCapabilityDriver.enable(GLFixedFunctionCapability.LIGHTING)