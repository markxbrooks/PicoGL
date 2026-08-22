"""ProjectionConfig and ApplicableState projection apply paths."""

from unittest.mock import patch

import numpy as np
from pyglm import glm

from picogl.backend.glm.glm import glm_mat4_to_np
from picogl.backend.legacy.core.camera.projection_state import (
    GLUProjectionState)
from picogl.backend.modern.core.camera.projection_state import (
    GLMProjectionState)
from picogl.core.camera import FOVY, ProjectionConfig


def test_projection_config_is_instantiable_and_equal():
    cfg = ProjectionConfig(aspect=16 / 9)
    assert cfg.fovy == 45.0
    assert cfg.near == 1.0
    assert cfg.far == 1000.0
    assert cfg.aspect == 16 / 9
    assert cfg == ProjectionConfig(
        fovy=45.0, aspect=16 / 9, near=1.0, far=1000.0
    )
    assert FOVY == 45.0
    assert ProjectionConfig().with_size(800, 400).aspect == 2.0
    assert ProjectionConfig.fovy == 45.0


def test_glu_projection_apply_is_cached():
    state = GLUProjectionState()
    cfg = ProjectionConfig(aspect=1.5)
    with (
        patch(
            "picogl.backend.legacy.core.camera.projection_state.gl_matrix_mode"
        ) as matrix_mode,
        patch(
            "picogl.backend.legacy.core.camera.projection_state."
            "gl_load_identity"
        ) as load_identity,
        patch(
            "picogl.backend.legacy.core.camera.projection_state."
            "glu_perspective"
        ) as perspective,
    ):
        state.apply(cfg)
        state.apply(cfg)
        assert perspective.call_count == 1
        perspective.assert_called_once_with(45.0, 1.5, 1.0, 1000.0)
        assert load_identity.call_count == 1
        assert matrix_mode.call_count == 2
        state.apply(cfg.with_aspect(2.0))
        assert perspective.call_count == 2


def test_glm_projection_matches_glm_perspective():
    state = GLMProjectionState()
    cfg = ProjectionConfig(aspect=1.5)
    state.apply(cfg)
    expected = glm.perspective(glm.radians(45.0), 1.5, 1.0, 1000.0)
    got = glm_mat4_to_np(state.matrix)
    want = glm_mat4_to_np(expected)
    np.testing.assert_allclose(got, want, rtol=1e-5)
    state.apply(cfg)
    assert state.matrix is not None
