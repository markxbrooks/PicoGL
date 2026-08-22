"""Cached GLU perspective projection (legacy matrix stack)."""

from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.driver.applicable_state import ApplicableState
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import gl_load_identity
from picogl.backend.glu.perspective import glu_perspective
from picogl.core.camera import ProjectionConfig


class GLUProjectionState(ApplicableState):
    """Applies ``ProjectionConfig`` via GLU onto ``GL_PROJECTION``."""

    def _do_apply(
        self,
        state: ProjectionConfig,
        prev: ProjectionConfig | None,
    ) -> None:
        del prev
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        glu_perspective(
            float(state.fovy),
            float(state.aspect),
            float(state.near),
            float(state.far),
        )
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    def _is_same(self, old: ProjectionConfig, new: ProjectionConfig) -> bool:
        return old == new
