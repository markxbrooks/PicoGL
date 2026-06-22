"""Tests for frame preparation helpers."""

import unittest
from unittest.mock import patch

from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.wrappers.frame import prepare_viewport


class RecordingFrame:
    def __init__(self, calls):
        self.calls = calls

    def viewport(self, x, y, width, height):
        self.calls.append(("viewport", x, y, width, height))

    def set_clear_color(self, color):
        self.calls.append(("set_clear_color", color))

    def clear(self, mask):
        self.calls.append(("clear", mask))


class RecordingDepth:
    def __init__(self, calls):
        self.calls = calls

    def set_depth_test(self, enabled):
        self.calls.append(("depth_test", enabled))


class RecordingCapabilities:
    def __init__(self, calls):
        self.calls = calls

    def enable(self, cap):
        self.calls.append(("enable", cap))


class RecordingBackend:
    def __init__(self):
        self.calls = []
        self.frame = RecordingFrame(self.calls)
        self.depth = RecordingDepth(self.calls)
        self.capabilities = RecordingCapabilities(self.calls)


class TestPrepareViewport(unittest.TestCase):
    def test_prepare_viewport_delegates_to_backend(self):
        backend = RecordingBackend()

        with patch("picogl.frame.platform.system", return_value="Darwin"):
            prepare_viewport(320, 240, backend)

        self.assertEqual(
            backend.calls,
            [
                ("viewport", 0, 0, 640, 480),
                ("depth_test", True),
                ("set_clear_color", (0.1, 0.1, 0.1, 1.0)),
                ("enable", GL_PROGRAM_POINT_SIZE),
                ("clear", GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER),
            ],
        )


if __name__ == "__main__":
    unittest.main()
