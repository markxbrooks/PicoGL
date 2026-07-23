from backend.gl.api.enable import gl_enable
from backend.gl.api.polygon_mode import gl_polygon_mode
from backend.gl.capability import GLMaterialFace, GLFixedFunctionCapability
from backend.gl.driver.capability import GLCapabilityDriver
from backend.gl.state.fill import GLFillMode
from renderer.legacy_glmesh import LegacyGLMesh


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