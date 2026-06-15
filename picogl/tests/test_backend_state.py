"""Tests for backend render-state helpers."""

import unittest
from unittest.mock import call, patch

from OpenGL.GL import GL_LIGHT0, GL_LINE, GL_MODELVIEW, GL_ONE, GL_POSITION, GL_ZERO
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_AMBIENT, GL_DIFFUSE,
                                          GL_FRONT_AND_BACK, GL_PROJECTION,
                                          GL_SHININESS, GL_SPECULAR)
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_CLIP_PLANE0, GL_CLIP_PLANE1

from picogl.backend.capability import GLMaterialFace, PhongMaterial
from picogl.backend.GL.backend import GLBackend, GLLegacyPipeline, GLRasterDriver
from picogl.backend.state import (
    BlendState,
    DepthState,
    DrawCommand,
    RasterState,
    RenderState,
    RenderStateApplier,
)


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def enable(self, cap):
        self.calls.append(("enable", cap))

    def disable(self, cap):
        self.calls.append(("disable", cap))

    def set_line_width(self, width):
        self.calls.append(("line_width", width))

    def set_polygon_mode(self, *args):
        self.calls.append(("polygon_mode", args))

    def set_depth_test(self, enabled):
        self.calls.append(("depth_test", enabled))

    def set_depth_write(self, enabled):
        self.calls.append(("depth_write", enabled))

    def set_blend(self, enabled):
        self.calls.append(("blend", enabled))

    def set_blend_func(self, src, dst):
        self.calls.append(("blend_func", src, dst))

    def set_cull_face(self, enabled):
        self.calls.append(("cull_face", enabled))

    def set_lighting(self, enabled):
        self.calls.append(("lighting", enabled))

    def apply_state(self, state):
        self.calls.append(("apply_state", state))

    def bind_texture(self, texture_id):
        self.calls.append(("bind_texture", texture_id))

    def draw_mesh(self, mesh, mode):
        self.calls.append(("draw_mesh", mesh, mode))


class FakeBinding:
    def bind_mesh(self, mesh):
        pass

    def draw(self, mesh, mode):
        pass


class TestRenderState(unittest.TestCase):
    def test_flat_constructor_matches_elmo_context_usage(self):
        state = RenderState(
            blend=True,
            depth_write=False,
            lighting=True,
            line_width=2.5,
            polygon_mode=GL_LINE,
        )

        self.assertTrue(state.blend)
        self.assertFalse(state.depth_write)
        self.assertTrue(state.depth_test)
        self.assertTrue(state.lighting)
        self.assertEqual(state.line_width, 2.5)
        self.assertEqual(state.polygon_mode, GL_LINE)
        self.assertEqual(state.raster, RasterState(GL_LINE, 2.5))
        self.assertEqual(state.depth, DepthState(test=True, write=False))

    def test_nested_constructor_inputs_are_flattened(self):
        state = RenderState(
            raster=RasterState(polygon_mode=GL_LINE, line_width=3.0),
            depth=DepthState(test=False, write=False),
            blend=BlendState(enabled=True, src=GL_ONE, dst=GL_ZERO),
            cull_face=True,
        )

        self.assertTrue(state.blend)
        self.assertEqual(state.blend_src, GL_ONE)
        self.assertEqual(state.blend_dst, GL_ZERO)
        self.assertFalse(state.depth_test)
        self.assertFalse(state.depth_write)
        self.assertEqual(state.line_width, 3.0)
        self.assertEqual(state.polygon_mode, GL_LINE)
        self.assertTrue(state.cull_face)


class TestRenderStateApplier(unittest.TestCase):
    def test_applies_state_once_and_skips_identical_state(self):
        backend = RecordingBackend()
        applier = RenderStateApplier(backend)
        state = RenderState(
            blend=True,
            depth_write=False,
            line_width=2.0,
            polygon_mode=GL_LINE,
            lighting=True,
        )

        applier.apply(state)
        first_call_count = len(backend.calls)
        applier.apply(state)

        self.assertEqual(len(backend.calls), first_call_count)
        self.assertIn(("blend", True), backend.calls)
        self.assertIn(("blend_func", state.blend_src, state.blend_dst), backend.calls)
        self.assertIn(("depth_write", False), backend.calls)
        self.assertIn(("lighting", True), backend.calls)

    def test_depth_state_applies_depth_not_blend(self):
        backend = RecordingBackend()
        depth = DepthState(test=False, write=False)

        depth.apply(state=type("State", (), {"backend": backend, "set_enabled": lambda _self, cap, enabled: backend.calls.append(("enabled", cap, enabled))})())

        call_names = [call[0] for call in backend.calls]
        self.assertIn("enabled", call_names)
        self.assertIn("depth_write", call_names)
        self.assertNotIn("blend", call_names)


class TestDrawCommand(unittest.TestCase):
    def test_draw_command_uses_backend_state_texture_and_draw_mesh(self):
        backend = RecordingBackend()
        mesh = object()
        state = RenderState(blend=True)
        command = DrawCommand(mesh=mesh, mode=GL_LINE, texture=7, state=state)

        command.execute(backend)

        self.assertEqual(
            backend.calls,
            [
                ("apply_state", state),
                ("bind_texture", 7),
                ("draw_mesh", mesh, GL_LINE),
            ],
        )

    def test_glbackend_exposes_state_api(self):
        backend = GLBackend(binding=FakeBinding())
        self.assertTrue(hasattr(backend, "apply_state"))
        self.assertTrue(hasattr(backend, "draw_command"))
        self.assertIsInstance(backend.raster, GLRasterDriver)
        self.assertIsInstance(backend.legacy, GLLegacyPipeline)

    def test_raster_driver_delegates_to_opengl(self):
        raster = GLRasterDriver()

        with (
            patch("picogl.backend.GL.backend.glLineWidth") as line_width,
            patch("picogl.backend.GL.backend.glPolygonMode") as polygon_mode,
        ):
            raster.set_line_width(2.0)
            raster.set_polygon_mode(GL_FRONT_AND_BACK, GL_LINE)

        line_width.assert_called_once_with(2.0)
        polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)

    def test_glbackend_polygon_mode_uses_raster_driver(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch.object(backend.raster, "set_line_width") as set_line_width,
            patch.object(backend.raster, "set_polygon_mode") as set_polygon_mode,
        ):
            backend.set_line_width(2.0)
            backend.set_polygon_mode(GL_FRONT_AND_BACK, GL_LINE)

        set_line_width.assert_called_once_with(2.0)
        set_polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)

    def test_legacy_pipeline_delegates_to_opengl(self):
        legacy = GLLegacyPipeline()
        material = PhongMaterial(
            ambient=(0.1, 0.2, 0.3, 1.0),
            diffuse=(0.4, 0.5, 0.6, 1.0),
            specular=(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch("picogl.backend.GL.backend.glMatrixMode") as matrix_mode,
            patch("picogl.backend.GL.backend.glLoadIdentity") as load_identity,
            patch("picogl.backend.GL.backend.gluPerspective") as perspective,
            patch("picogl.backend.GL.backend.glTranslatef") as translate,
            patch("picogl.backend.GL.backend.glLightfv") as lightfv,
            patch("picogl.backend.GL.backend.glMaterialfv") as materialfv,
            patch("picogl.backend.GL.backend.glMaterialf") as materialf,
        ):
            legacy.set_projection(45.0, 1.5, 0.1, 1000.0)
            legacy.translate(1, 2, 3)
            legacy.set_light([0.0, 0.0, 10.0, 1.0])
            legacy.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        self.assertEqual(matrix_mode.call_args_list, [call(GL_PROJECTION), call(GL_MODELVIEW)])
        load_identity.assert_called_once_with()
        perspective.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)
        translate.assert_called_once_with(1.0, 2.0, 3.0)
        lightfv.assert_called_once_with(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
        self.assertEqual(
            materialfv.call_args_list,
            [
                call(GL_FRONT_AND_BACK, GL_AMBIENT, material.ambient),
                call(GL_FRONT_AND_BACK, GL_DIFFUSE, material.diffuse),
                call(GL_FRONT_AND_BACK, GL_SPECULAR, material.specular),
            ],
        )
        materialf.assert_called_once_with(
            GL_FRONT_AND_BACK,
            GL_SHININESS,
            material.shininess,
        )

    def test_glbackend_fixed_function_uses_legacy_pipeline(self):
        backend = GLBackend(binding=FakeBinding())
        material = PhongMaterial(
            ambient=(0.1, 0.2, 0.3, 1.0),
            diffuse=(0.4, 0.5, 0.6, 1.0),
            specular=(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch.object(backend.legacy, "set_projection") as set_projection,
            patch.object(backend.legacy, "translate") as translate,
            patch.object(backend.legacy, "set_light") as set_light,
            patch.object(backend.legacy, "set_material") as set_material,
        ):
            backend.set_perspective_projection(45.0, 1.5, 0.1, 1000.0)
            backend.translate(1, 2, 3)
            backend.set_light_position([0.0, 0.0, 10.0, 1.0])
            backend.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        set_projection.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)
        translate.assert_called_once_with(1, 2, 3)
        set_light.assert_called_once_with(
            [0.0, 0.0, 10.0, 1.0],
            light=GL_LIGHT0,
        )
        set_material.assert_called_once_with(GLMaterialFace.FRONT_AND_BACK, material)

    def test_glbackend_fixed_function_delegates_to_opengl(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch("picogl.backend.GL.backend.glViewport") as viewport,
            patch("picogl.backend.GL.backend.glLoadIdentity") as load_identity,
            patch("picogl.backend.GL.backend.glTranslatef") as translate,
            patch("picogl.backend.GL.backend.glLightfv") as lightfv,
            patch("picogl.backend.GL.backend.glEnable") as enable,
            patch("picogl.backend.GL.backend.glDisable") as disable,
            patch("picogl.backend.GL.backend.glClearColor") as clear_color,
        ):
            backend.viewport(1, 2, 3, 4)
            backend.load_identity()
            backend.translate(1, 2, 3)
            backend.set_light_position([0.0, 0.0, 10.0, 1.0])
            backend.enable_clip_plane0()
            backend.disable_clip_plane1()
            backend.set_clear_color((0.1, 0.2, 0.3, 1.0))

        viewport.assert_called_once_with(1, 2, 3, 4)
        load_identity.assert_called_once_with()
        translate.assert_called_once_with(1.0, 2.0, 3.0)
        lightfv.assert_called_once_with(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
        enable.assert_called_once_with(GL_CLIP_PLANE0)
        disable.assert_called_once_with(GL_CLIP_PLANE1)
        clear_color.assert_called_once_with(0.1, 0.2, 0.3, 1.0)

    def test_glbackend_perspective_projection_delegates_to_opengl(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch("picogl.backend.GL.backend.glMatrixMode") as matrix_mode,
            patch("picogl.backend.GL.backend.glLoadIdentity") as load_identity,
            patch("picogl.backend.GL.backend.gluPerspective") as perspective,
        ):
            backend.set_perspective_projection(45.0, 1.5, 0.1, 1000.0)

        self.assertEqual(
            matrix_mode.call_args_list,
            [
                call(GL_PROJECTION),
                call(GL_MODELVIEW),
            ],
        )
        load_identity.assert_called_once_with()
        perspective.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)

    def test_glbackend_set_material_delegates_to_opengl(self):
        backend = GLBackend(binding=FakeBinding())
        material = PhongMaterial(
            ambient=(0.1, 0.2, 0.3, 1.0),
            diffuse=(0.4, 0.5, 0.6, 1.0),
            specular=(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch("picogl.backend.GL.backend.glMaterialfv") as materialfv,
            patch("picogl.backend.GL.backend.glMaterialf") as materialf,
        ):
            backend.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        self.assertEqual(
            materialfv.call_args_list,
            [
                call(GL_FRONT_AND_BACK, GL_AMBIENT, material.ambient),
                call(GL_FRONT_AND_BACK, GL_DIFFUSE, material.diffuse),
                call(GL_FRONT_AND_BACK, GL_SPECULAR, material.specular),
            ],
        )
        materialf.assert_called_once_with(
            GL_FRONT_AND_BACK,
            GL_SHININESS,
            material.shininess,
        )


if __name__ == "__main__":
    unittest.main()
