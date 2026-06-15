"""Tests for frame preparation helpers."""

import unittest
from unittest.mock import patch

from OpenGL.raw.GL.VERSION.GL_3_2 import GL_PROGRAM_POINT_SIZE

from picogl.frame import prepare_viewport


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def viewport(self, x, y, width, height):
        self.calls.append(("viewport", x, y, width, height))

    def enable_depth_test(self):
        self.calls.append(("enable_depth_test",))

    def set_clear_color(self, color):
        self.calls.append(("set_clear_color", color))

    def enable(self, cap):
        self.calls.append(("enable", cap))

    def clear_background(self):
        self.calls.append(("clear_background",))


class TestPrepareViewport(unittest.TestCase):
    def test_prepare_viewport_delegates_to_backend(self):
        backend = RecordingBackend()

        with patch("picogl.frame.platform.system", return_value="Darwin"):
            prepare_viewport(320, 240, backend)

        self.assertEqual(
            backend.calls,
            [
                ("viewport", 0, 0, 640, 480),
                ("enable_depth_test",),
                ("set_clear_color", (0.1, 0.1, 0.1, 1.0)),
                ("enable", GL_PROGRAM_POINT_SIZE),
                ("clear_background",),
            ],
        )


if __name__ == "__main__":
    unittest.main()
