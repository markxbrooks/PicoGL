"""Tests for state-preserving scoped OpenGL context managers."""

from unittest import TestCase
from unittest.mock import call, patch

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POLYGON_MODE

from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLFace, GLFillMode
from picogl.backend.gl.state.scoped import gl_disabled, gl_capability
from picogl.polygon.mode import gl_polygon_mode_context


class ScopedCapabilityTests(TestCase):
    def test_disabled_restores_when_was_enabled(self):
        with patch(
            "picogl.backend.gl.state.scoped.gl_is_enabled",
            return_value=True,
        ) as is_enabled, patch(
            "picogl.backend.gl.state.scoped.gl_disable",
        ) as gl_disable, patch(
            "picogl.backend.gl.state.scoped.gl_enable",
        ) as gl_enable:
            with gl_disabled(GLFixedFunctionCapability.LIGHTING):
                pass

        is_enabled.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)
        gl_disable.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)
        gl_enable.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)

    def test_disabled_restores_disabled_when_already_disabled(self):
        with patch(
            "picogl.backend.gl.state.scoped.gl_is_enabled",
            return_value=False,
        ), patch(
            "picogl.backend.gl.state.scoped.gl_disable",
        ) as gl_disable, patch(
            "picogl.backend.gl.state.scoped.gl_enable",
        ) as gl_enable:
            with gl_disabled(GLFixedFunctionCapability.LIGHTING):
                pass

        gl_disable.assert_has_calls(
            [
                call(GLFixedFunctionCapability.LIGHTING),
                call(GLFixedFunctionCapability.LIGHTING),
            ]
        )
        gl_enable.assert_not_called()

    def test_gl_capability_enables_when_was_disabled(self):
        with patch(
            "picogl.backend.gl.state.scoped.gl_is_enabled",
            return_value=False,
        ), patch(
            "picogl.backend.gl.state.scoped.gl_enable",
        ) as gl_enable, patch(
            "picogl.backend.gl.state.scoped.gl_disable",
        ) as gl_disable:
            with gl_capability(GLFixedFunctionCapability.LIGHTING, True):
                pass

        gl_enable.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)
        gl_disable.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)

    def test_gl_capability_restores_when_was_enabled(self):
        with patch(
            "picogl.backend.gl.state.scoped.gl_is_enabled",
            return_value=True,
        ), patch(
            "picogl.backend.gl.state.scoped.gl_enable",
        ) as gl_enable, patch(
            "picogl.backend.gl.state.scoped.gl_disable",
        ) as gl_disable:
            with gl_capability(GLFixedFunctionCapability.LIGHTING, True):
                pass

        gl_enable.assert_has_calls(
            [
                call(GLFixedFunctionCapability.LIGHTING),
                call(GLFixedFunctionCapability.LIGHTING),
            ]
        )
        gl_disable.assert_not_called()


class ScopedPolygonModeTests(TestCase):
    def test_polygon_mode_context_restores_previous_modes(self):
        with patch(
            "picogl.polygon.mode.gl_get_integerv",
            return_value=[GLFillMode.LINE, GLFillMode.FILL],
        ) as gl_get_integerv, patch(
            "picogl.polygon.mode.gl_polygon_mode",
        ) as gl_polygon_mode:
            with gl_polygon_mode_context(GLFillMode.FILL):
                pass

        gl_get_integerv.assert_called_once_with(GL_POLYGON_MODE)
        gl_polygon_mode.assert_has_calls(
            [
                call(GLFace.FRONT_AND_BACK, GLFillMode.FILL),
                call(GLFace.FRONT, GLFillMode.LINE),
                call(GLFace.BACK, GLFillMode.FILL),
            ]
        )
