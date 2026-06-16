"""Tests for backend render-state helpers."""

import unittest
from unittest.mock import call, patch

from OpenGL.GL import (
    GL_BLEND,
    GL_CULL_FACE,
    GL_DEPTH_TEST,
    GL_FLOAT,
    GL_LIGHT0,
    GL_LIGHTING,
    GL_LINE,
    GL_MODELVIEW,
    GL_ONE,
    GL_POSITION,
    GL_TEXTURE_2D,
    GL_TEXTURE_COORD_ARRAY,
    GL_UNSIGNED_INT,
    GL_ZERO,
    GL_COLOR_ARRAY,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
)
from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_AMBIENT, GL_DIFFUSE,
                                          GL_FRONT_AND_BACK, GL_PROJECTION,
                                          GL_SHININESS, GL_SPECULAR)
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_CLIP_PLANE0, GL_CLIP_PLANE1

from picogl.backend.capability import GLMaterialFace, PhongMaterial
from picogl.backend.GL.backend import (
    GLBackend,
)
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline
from picogl.backend.legacy.core.attribute_binder import LegacyAttributeBinder
from picogl.backend.GL.driver.texture import GLTextureSystem
from picogl.backend.GL.driver.geometry import GLGeometryDriver
from picogl.backend.GL.driver.blend import GLBlendDriver
from picogl.backend.GL.driver.depth import GLDepthDriver
from picogl.backend.GL.driver.capability import GLCapabilityDriver
from picogl.backend.GL.driver.raster import GLRasterDriver
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


class RecordingBinding:
    def __init__(self):
        self.calls = []

    def bind_mesh(self, mesh):
        self.calls.append(("bind_mesh", mesh))

    def draw(self, mesh, mode):
        self.calls.append(("draw", mesh, mode))


class FakeTextureDriver:
    def __init__(self):
        self.calls = []

    def create(self, tex):
        self.calls.append(("create", tex))
        tex.handle = 42

    def bind(self, tex):
        self.calls.append(("bind", tex))

    def initialize(self, tex):
        self.calls.append(("initialize", tex))


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
            patch("picogl.backend.GL.driver.raster.glLineWidth") as line_width,
            patch("picogl.backend.GL.driver.raster.glPolygonMode") as polygon_mode,
            patch("picogl.backend.GL.driver.raster.glPointSize") as point_size,
            patch(
                "picogl.backend.GL.driver.raster.glGetFloatv",
                return_value=(1.0, 10.0),
            ) as get_float,
            patch("picogl.backend.GL.driver.raster.glPolygonOffset") as polygon_offset,
        ):
            raster.set_line_width(2.0)
            raster.set_polygon_mode(GL_FRONT_AND_BACK, GL_LINE)
            raster.set_point_size(3.0)
            raster.set_clamped_point_size(12.0)
            raster.set_polygon_offset(-1.0, -1.0)

        line_width.assert_called_once_with(2.0)
        polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)
        self.assertEqual(point_size.call_args_list, [call(3.0), call(10.0)])
        get_float.assert_called_once()
        polygon_offset.assert_called_once_with(-1.0, -1.0)

    def test_state_subsystem_drivers_delegate_to_opengl(self):
        capabilities = GLCapabilityDriver()
        depth = GLDepthDriver(capabilities)
        blend = GLBlendDriver(capabilities)

        with (
            patch("picogl.backend.GL.backend.glEnable") as enable,
            patch("picogl.backend.GL.backend.glDisable") as disable,
            patch("picogl.backend.GL.backend.glIsEnabled", return_value=True) as is_enabled,
            patch("picogl.backend.GL.backend.glDepthMask") as depth_mask,
            patch("picogl.backend.GL.backend.glDepthFunc") as depth_func,
            patch("picogl.backend.GL.backend.glBlendFunc") as blend_func,
        ):
            capabilities.enable(GL_CULL_FACE)
            capabilities.disable(GL_LIGHTING)
            self.assertTrue(capabilities.is_enabled(GL_DEPTH_TEST))
            depth.set_depth_test(True)
            depth.set_depth_write(False)
            depth.set_depth_func_gl_less()
            blend.set_blend(True)
            blend.set_blend_func(GL_ONE, GL_ZERO)

        self.assertEqual(
            enable.call_args_list,
            [call(GL_CULL_FACE), call(GL_DEPTH_TEST), call(GL_BLEND)],
        )
        disable.assert_called_once_with(GL_LIGHTING)
        is_enabled.assert_called_once_with(GL_DEPTH_TEST)
        depth_mask.assert_called_once_with(False)
        depth_func.assert_called_once()
        blend_func.assert_called_once_with(GL_ONE, GL_ZERO)

    def test_glbackend_state_facade_uses_state_subsystems(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch.object(backend.capabilities, "enable") as enable,
            patch.object(backend.capabilities, "disable") as disable,
            patch.object(backend.capabilities, "is_enabled", return_value=True) as is_enabled,
            patch.object(backend.capabilities, "set_enabled") as set_enabled,
            patch.object(backend.depth, "set_depth_test") as set_depth_test,
            patch.object(backend.depth, "set_depth_write") as set_depth_write,
            patch.object(backend.depth, "set_depth_func_gl_less") as set_depth_func,
            patch.object(backend.blend, "set_blend") as set_blend,
            patch.object(backend.blend, "set_blend_func") as set_blend_func,
            patch.object(backend.blend, "setup_blending") as setup_blending,
        ):
            backend.enable(GL_CULL_FACE)
            backend.disable(GL_LIGHTING)
            self.assertTrue(backend.is_enabled(GL_DEPTH_TEST))
            backend.set_depth_test(True)
            backend.set_depth_write(False)
            backend.set_depth_func_gl_less()
            backend.set_blend(True)
            backend.set_blend_func(GL_ONE, GL_ZERO)
            backend.setup_blending()
            backend.set_cull_face(True)
            backend.set_lighting(False)

        enable.assert_called_once_with(GL_CULL_FACE)
        disable.assert_called_once_with(GL_LIGHTING)
        is_enabled.assert_called_once_with(GL_DEPTH_TEST)
        set_depth_test.assert_called_once_with(True)
        set_depth_write.assert_called_once_with(False)
        set_depth_func.assert_called_once_with()
        set_blend.assert_called_once_with(True)
        set_blend_func.assert_called_once_with(GL_ONE, GL_ZERO)
        setup_blending.assert_called_once_with()
        self.assertEqual(
            set_enabled.call_args_list,
            [call(GL_CULL_FACE, True), call(GL_LIGHTING, False)],
        )

    def test_glbackend_polygon_mode_uses_raster_driver(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch.object(backend.raster, "set_line_width") as set_line_width,
            patch.object(backend.raster, "set_polygon_mode") as set_polygon_mode,
            patch.object(backend.raster, "set_point_size") as set_point_size,
            patch.object(
                backend.raster,
                "set_clamped_point_size",
            ) as set_clamped_point_size,
            patch.object(backend.raster, "set_polygon_offset") as set_polygon_offset,
        ):
            backend.set_line_width(2.0)
            backend.set_polygon_mode(GL_FRONT_AND_BACK, GL_LINE)
            backend.set_point_size(3.0)
            backend.set_clamped_point_size(4.0)
            backend.set_polygon_offset(-1.0, -1.0)

        set_line_width.assert_called_once_with(2.0)
        set_polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)
        set_point_size.assert_called_once_with(3.0)
        set_clamped_point_size.assert_called_once_with(4.0)
        set_polygon_offset.assert_called_once_with(-1.0, -1.0)

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

    def test_geometry_driver_delegates_to_binding_and_draw_elements(self):
        binding = RecordingBinding()
        geometry = GLGeometryDriver(binding)
        mesh = object()

        with (
            patch("picogl.backend.GL.driver.geometry.glDrawElements") as draw_elements,
            patch("picogl.backend.GL.driver.geometry.glDrawArrays") as draw_arrays,
            patch("picogl.backend.GL.driver.geometry.glBindVertexArray") as bind_vao,
        ):
            geometry.draw_mesh(mesh, GL_LINE)
            geometry.draw_elements(GL_LINE, [0, 1, 2])
            geometry.draw_bound_elements(GL_LINE, 4, GL_UNSIGNED_INT, None)
            geometry.draw_arrays(GL_LINE, 2, 5)
            geometry.draw_arrays_bound_vao(9, GL_LINE, 1, 6)

        self.assertEqual(binding.calls, [("bind_mesh", mesh), ("draw", mesh, GL_LINE)])
        self.assertEqual(
            draw_elements.call_args_list,
            [
                call(GL_LINE, 3, GL_UNSIGNED_INT, [0, 1, 2]),
                call(GL_LINE, 4, GL_UNSIGNED_INT, None),
            ],
        )
        self.assertEqual(
            draw_arrays.call_args_list,
            [call(GL_LINE, 2, 5), call(GL_LINE, 1, 6)],
        )
        self.assertEqual(bind_vao.call_args_list, [call(9), call(0)])

    def test_texture_system_owns_texture_lifecycle(self):
        driver = FakeTextureDriver()
        textures = GLTextureSystem(driver=driver)

        with (
            patch("picogl.backend.GL.backend.glBindTexture") as bind_texture,
            patch("picogl.backend.GL.backend.glDeleteTextures") as delete_textures,
        ):
            handle = textures.create_texture(4, 5, data=None)
            textures.bind_texture(7)
            textures.delete_texture(7)

        self.assertEqual(handle, 42)
        self.assertEqual([call[0] for call in driver.calls], ["create", "bind", "initialize"])
        self.assertEqual(driver.calls[0][1].spec.width, 4)
        self.assertEqual(driver.calls[0][1].spec.height, 5)
        bind_texture.assert_called_once_with(GL_TEXTURE_2D, 7)
        delete_textures.assert_called_once_with([7])

    def test_legacy_attribute_binder_delegates_to_client_state_calls(self):
        binder = LegacyAttributeBinder()
        data = object()

        with (
            patch("picogl.backend.GL.backend.glEnableClientState") as enable_client,
            patch("picogl.backend.GL.backend.glVertexPointer") as vertex_pointer,
            patch("picogl.backend.GL.backend.glNormalPointer") as normal_pointer,
            patch("picogl.backend.GL.backend.glColorPointer") as color_pointer,
            patch("picogl.backend.GL.backend.glTexCoordPointer") as texcoord_pointer,
        ):
            binder.enable_vertex_array()
            binder.set_vertex_pointer(data)
            binder.enable_normal_array()
            binder.set_normal_pointer(data)
            binder.enable_color_array()
            binder.set_color_pointer(data, 4)
            binder.enable_texcoord_array()
            binder.set_texcoord_pointer(data)

        self.assertEqual(
            enable_client.call_args_list,
            [
                call(GL_VERTEX_ARRAY),
                call(GL_NORMAL_ARRAY),
                call(GL_COLOR_ARRAY),
                call(GL_TEXTURE_COORD_ARRAY),
            ],
        )
        vertex_pointer.assert_called_once_with(3, GL_FLOAT, 0, data)
        normal_pointer.assert_called_once_with(GL_FLOAT, 0, data)
        color_pointer.assert_called_once_with(4, GL_FLOAT, 0, data)
        texcoord_pointer.assert_called_once_with(2, GL_FLOAT, 0, data)

    def test_glbackend_geometry_texture_and_attribute_facades_use_subsystems(self):
        backend = GLBackend(binding=FakeBinding())
        mesh = object()
        data = object()

        with (
            patch.object(backend.geometry, "draw_mesh") as draw_mesh,
            patch.object(backend.geometry, "draw_elements") as draw_elements,
            patch.object(backend.geometry, "draw_bound_elements") as draw_bound_elements,
            patch.object(backend.geometry, "draw_arrays") as draw_arrays,
            patch.object(
                backend.geometry,
                "draw_arrays_bound_vao",
            ) as draw_arrays_bound_vao,
            patch.object(backend.textures, "create_texture", return_value=9) as create_texture,
            patch.object(backend.textures, "bind_texture") as bind_texture,
            patch.object(backend.textures, "delete_texture") as delete_texture,
            patch.object(backend.attributes, "enable_vertex_array") as enable_vertex_array,
            patch.object(backend.attributes, "set_vertex_pointer") as set_vertex_pointer,
            patch.object(backend.attributes, "enable_normal_array") as enable_normal_array,
            patch.object(backend.attributes, "set_normal_pointer") as set_normal_pointer,
            patch.object(backend.attributes, "enable_color_array") as enable_color_array,
            patch.object(backend.attributes, "set_color_pointer") as set_color_pointer,
            patch.object(backend.attributes, "enable_texcoord_array") as enable_texcoord_array,
            patch.object(backend.attributes, "set_texcoord_pointer") as set_texcoord_pointer,
        ):
            backend.draw_mesh(mesh, GL_LINE)
            backend.draw_elements(GL_LINE, [0, 1, 2])
            backend.draw_bound_elements(GL_LINE, 4, GL_UNSIGNED_INT, None)
            backend.draw_arrays(GL_LINE, 1, 6)
            backend.draw_arrays_bound_vao(9, GL_LINE, 2, 7)
            self.assertEqual(backend.create_texture(4, 5, None), 9)
            backend.bind_texture(7)
            backend.delete_texture(7)
            backend.enable_vertex_array()
            backend.set_vertex_pointer(data)
            backend.enable_normal_array()
            backend.set_normal_pointer(data)
            backend.enable_color_array()
            backend.set_color_pointer(data, 4)
            backend.enable_texcoord_array()
            backend.set_texcoord_pointer(data)

        draw_mesh.assert_called_once_with(mesh, GL_LINE)
        draw_elements.assert_called_once_with(GL_LINE, [0, 1, 2])
        draw_bound_elements.assert_called_once_with(GL_LINE, 4, GL_UNSIGNED_INT, None)
        draw_arrays.assert_called_once_with(GL_LINE, 1, 6)
        draw_arrays_bound_vao.assert_called_once_with(9, GL_LINE, 2, 7)
        create_texture.assert_called_once_with(4, 5, None)
        bind_texture.assert_called_once_with(7)
        delete_texture.assert_called_once_with(7)
        enable_vertex_array.assert_called_once_with()
        set_vertex_pointer.assert_called_once_with(data)
        enable_normal_array.assert_called_once_with()
        set_normal_pointer.assert_called_once_with(data)
        enable_color_array.assert_called_once_with()
        set_color_pointer.assert_called_once_with(data, 4)
        enable_texcoord_array.assert_called_once_with()
        set_texcoord_pointer.assert_called_once_with(data)

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
