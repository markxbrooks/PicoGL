"""Unit tests for framebuffer-based device_pixel_ratio."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from picogl.backend.gl.api import dpr as dpr_module
from picogl.backend.gl.enums.frame import GLFrameBufferObjectType


@patch.object(dpr_module, "framebuffer_attachment_size", return_value=(800, 600))
def test_device_pixel_ratio_averages_axes(_mock_size):
    assert dpr_module.device_pixel_ratio(400, 300) == pytest.approx(2.0)


@patch.object(dpr_module, "framebuffer_attachment_size", return_value=None)
def test_device_pixel_ratio_returns_one_when_unsupported(_mock_size):
    assert dpr_module.device_pixel_ratio(400, 300) == pytest.approx(1.0)


def test_device_pixel_ratio_returns_one_for_empty_logical_size():
    assert dpr_module.device_pixel_ratio(0, 300) == pytest.approx(1.0)
    assert dpr_module.device_pixel_ratio(400, 0) == pytest.approx(1.0)


@patch.object(dpr_module, "gl_get_tex_level_parameteriv", side_effect=[800, 600])
@patch.object(dpr_module, "gl_bind_texture")
@patch.object(dpr_module, "gl_get_integerv", return_value=0)
@patch.object(
    dpr_module,
    "gl_get_framebuffer_attachment_parameteriv",
    side_effect=[int(GLFrameBufferObjectType.TEXTURE), 42],
)
def test_framebuffer_attachment_size_from_texture(
    _mock_attach,
    _mock_get_int,
    mock_bind,
    _mock_tex_level,
):
    assert dpr_module.framebuffer_attachment_size() == (800, 600)
    assert mock_bind.call_count == 2


@patch.object(dpr_module, "gl_get_renderbuffer_parameteriv", side_effect=[800, 600])
@patch.object(dpr_module, "gl_bind_renderbuffer")
@patch.object(dpr_module, "gl_get_integerv", return_value=0)
@patch.object(
    dpr_module,
    "gl_get_framebuffer_attachment_parameteriv",
    side_effect=[int(GLFrameBufferObjectType.RENDERBUFFER), 7],
)
def test_framebuffer_attachment_size_from_renderbuffer(
    _mock_attach,
    _mock_get_int,
    mock_bind,
    _mock_rb,
):
    assert dpr_module.framebuffer_attachment_size() == (800, 600)
    assert mock_bind.call_count == 2
