"""Cached GLM perspective projection (no GL matrix stack)."""

from pyglm import glm

from picogl.backend.gl.driver.applicable_state import ApplicableState
from picogl.core.camera import ProjectionConfig


class GLMProjectionState(ApplicableState):
    """Applies ``ProjectionConfig`` by computing a GLM perspective matrix."""

    def __init__(self) -> None:
        super().__init__()
        self.matrix: glm.mat4 | None = None

    def _do_apply(
        self,
        state: ProjectionConfig,
        prev: ProjectionConfig | None,
    ) -> None:
        del prev
        self.matrix = state.matrix()

    def _is_same(self, old: ProjectionConfig, new: ProjectionConfig) -> bool:
        return old == new
