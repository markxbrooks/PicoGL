"""Tests for GLUT MouseInteraction drag state."""

import unittest

from picogl.ui.backend.glut.mouse import MouseInteraction, RotationInteraction


class TestMouseInteraction(unittest.TestCase):
    def test_drag_ignored_until_press(self):
        mouse = MouseInteraction()
        self.assertIsNone(mouse.drag(10, 20))

    def test_press_drag_updates_last_and_delta(self):
        mouse = MouseInteraction()
        mouse.press(10, 20)
        self.assertEqual(mouse.drag(14, 17), (4, -3))
        self.assertEqual((mouse.last_x, mouse.last_y), (14, 17))

    def test_release_stops_dragging(self):
        mouse = MouseInteraction()
        mouse.press(0, 0)
        mouse.release()
        self.assertFalse(mouse.dragging)
        self.assertIsNone(mouse.drag(5, 5))


class TestRotationInteraction(unittest.TestCase):
    def test_drag_ignored_until_press(self):
        rotation = RotationInteraction()
        self.assertIsNone(rotation.drag(10, 20))

    def test_drag_updates_rotation_from_delta(self):
        rotation = RotationInteraction()
        rotation.press(10, 20)
        self.assertEqual(rotation.drag(14, 17), (-1.5, 2.0))
        self.assertEqual(rotation.x, -1.5)
        self.assertEqual(rotation.y, 2.0)

    def test_reset_and_clamp_x(self):
        rotation = RotationInteraction()
        rotation.x = 120.0
        rotation.y = 15.0
        rotation.clamp_x()
        self.assertEqual(rotation.x, 90.0)
        rotation.reset()
        self.assertEqual((rotation.x, rotation.y), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
