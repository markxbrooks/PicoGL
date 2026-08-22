"""Tests for LegacyRenderer base class."""

from unittest import TestCase

from picogl.backend.legacy.core.renderer import LegacyRenderer
from picogl.examples.legacy_cube_minimal import MinimalCubeRenderer
from picogl.examples.legacy_teapot import LegacyTeapotRenderer


class LegacyRendererTests(TestCase):
    def test_base_class_is_abstract(self):
        with self.assertRaises(TypeError):
            LegacyRenderer()

    def test_subclasses_concrete(self):
        teapot = LegacyTeapotRenderer()
        cube = MinimalCubeRenderer()
        self.assertIsInstance(teapot, LegacyRenderer)
        self.assertIsInstance(cube, LegacyRenderer)
        self.assertEqual(len(cube.vertices), 36)
