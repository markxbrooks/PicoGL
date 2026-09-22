"""Tests for ctypes buffer payloads used by glBufferData uploads."""

from __future__ import annotations

from ctypes import Array

from OpenGL.GL import GLfloat, GLushort
from picogl.backend.gl.api.buffer.upload import _ctypes_array


def test_ctypes_array_is_instance_not_type() -> None:
    payload = _ctypes_array(GLfloat, [1.0, 2.0, 3.0])
    assert isinstance(payload, Array)
    assert not isinstance(payload, type)
    assert len(payload) == 3
    assert payload[0] == 1.0
    assert payload[2] == 3.0


def test_ctypes_ushort_array_round_trip() -> None:
    payload = _ctypes_array(GLushort, [0, 1, 2, 65535])
    assert list(payload) == [0, 1, 2, 65535]
