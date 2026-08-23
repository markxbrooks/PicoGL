"""
draw legacy mesh
"""

from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.gl.state.scoped import gl_disabled
from picogl.polygon.mode import gl_polygon_mode
from picogl.renderer.legacy_glmesh import LegacyGLMesh


def draw_legacy_mesh(mesh: LegacyGLMesh, wireframe_mode):
    """draw legacy mesh"""
    if wireframe_mode:
        with gl_disabled(GLFixedFunctionCapability.LIGHTING):
            with gl_polygon_mode(GLFillMode.LINE):
                mesh.draw()
        return

    mesh.draw()
