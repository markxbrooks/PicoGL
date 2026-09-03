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
    GL_UNSIGNED_INT,
    GL_ZERO,
)
from OpenGL.raw.GL.VERSION.GL_1_0 import (
    GL_AMBIENT,
    GL_DIFFUSE,
    GL_FRONT_AND_BACK,
    GL_PROJECTION,
    GL_SHININESS,
    GL_SPECULAR,
)
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.capability import (
    GLBlendFactor,
    GLFixedFunctionCapability,
    GLMaterialFace,
    GLPipelineCapability,
)
from picogl.backend.gl.driver.blend import GLBlendDriver
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.driver.depth import GLDepthDriver
from picogl.backend.gl.driver.frame import GLFrameDriver
from picogl.backend.gl.driver.geometry import GLGeometryDriver
from picogl.backend.gl.driver.raster import GLRasterDriver, resolve_polygon_mode_args
from picogl.backend.gl.driver.texture import GLTextureSystem
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.state.fill import GLFace, GLFillMode, GLLightParameter
from picogl.backend.legacy.core.attribute_binder import LegacyAttributeBinder
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline
from picogl.backend.state import (
    BlendState,
    DepthState,
    DrawCommand,
    GLClipPlaneState,
    RasterState,
    RenderState,
    RenderStateApplier,
    gl_value,
)
from picogl.core.polygon.mode import PolygonMode
from picogl.core.rgbcolor import RGBAColor
from picogl.core.viewport import Viewport


class _RecordingRaster:
    def __init__(self, calls):
        self.calls = calls

    def set_line_width(self, width):
        self.calls.append(("line_width", width))

    def set_polygon_mode(self, face, mode):
        self.calls.append(("polygon_mode", face, mode))

    def apply(self, state):
        self.set_line_width(state.line_width)
        self.set_polygon_mode(GLFace.FRONT_AND_BACK, gl_value(state.gl_polygon_mode))
        if state.polygon_offset != (0.0, 0.0):
            self.calls.append(("polygon_offset", state.polygon_offset))
        if state.point_size is not None:
            self.calls.append(("point_size", state.point_size))


class _RecordingDepth:
    def __init__(self, calls):
        self.calls = calls

    def set_depth_test(self, enabled):
        self.calls.append(("depth_test", enabled))

    def set_depth_write(self, enabled):
        self.calls.append(("depth_write", enabled))

    def apply(self, state):
        self.set_depth_test(state.test)
        self.set_depth_write(state.write)


class _RecordingBlend:
    def __init__(self, calls):
        self.calls = calls

    def set_blend(self, enabled):
        self.calls.append(("blend", enabled))

    def set_blend_func(self, src, dst):
        self.calls.append(("blend_func", src, dst))

    def apply(self, state):
        self.set_blend(state.enabled)
        if state.enabled:
            self.set_blend_func(gl_value(state.src), gl_value(state.dst))


class _RecordingCapabilities:
    def __init__(self, calls):
        self.calls = calls

    def set_enabled(self, cap, enabled):
        self.calls.append(("enabled", cap, enabled))


class RecordingBackend:
    def __init__(self):
        self.calls = []
        self.blend = _RecordingBlend(self.calls)
        self.depth = _RecordingDepth(self.calls)
        self.raster = _RecordingRaster(self.calls)
        self.capabilities = _RecordingCapabilities(self.calls)

    def enable(self, cap):
        self.calls.append(("enable", cap))

    def disable(self, cap):
        self.calls.append(("disable", cap))

    def set_line_width(self, width):
        self.calls.append(("line_width", width))

    def set_polygon_mode(self, *args):
        self.calls.append(("polygon_mode", args))

    def set_depth_write(self, enabled):
        self.calls.append(("depth_write", enabled))

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
        self.assertEqual(
            state.raster, RasterState(polygon_mode=GL_LINE, line_width=2.5)
        )
        self.assertEqual(state.depth, DepthState(test=True, write=False))

    def test_default_constructor_stores_semantic_values(self):
        state = RenderState()

        self.assertEqual(state.blend_src, GLBlendFactor.SRC_ALPHA)
        self.assertEqual(state.blend_dst, GLBlendFactor.ONE_MINUS_SRC_ALPHA)
        self.assertEqual(state.polygon_mode, GLFillMode.FILL)

    def test_nested_constructor_inputs_are_flattened(self):
        state = RenderState(
            raster=RasterState(polygon_mode=GL_LINE, line_width=3.0),
            depth=DepthState(test=False, write=False),
            blend=BlendState(
                enabled=True,
                src=GLBlendFactor.ONE,
                dst=GLBlendFactor.ZERO,
            ),
            cull_face=True,
        )

        self.assertTrue(state.blend)
        self.assertEqual(state.blend_src, GLBlendFactor.ONE)
        self.assertEqual(state.blend_dst, GLBlendFactor.ZERO)
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
            blend_src=GLBlendFactor.ONE,
            blend_dst=GLBlendFactor.ZERO,
            depth_write=False,
            line_width=2.0,
            polygon_mode=GLFillMode.LINE,
            lighting=True,
        )

        applier.apply(state)
        first_call_count = len(backend.calls)
        applier.apply(state)

        self.assertEqual(len(backend.calls), first_call_count)
        self.assertIn(("blend", True), backend.calls)
        self.assertIn(("blend_func", GL_ONE, GL_ZERO), backend.calls)
        self.assertIn(("polygon_mode", GLFace.FRONT_AND_BACK, GL_LINE), backend.calls)
        self.assertIn(("depth_write", False), backend.calls)
        self.assertIn(
            ("enabled", GLFixedFunctionCapability.LIGHTING, True),
            backend.calls,
        )

        applier.apply(RenderState(lighting=False))
        self.assertNotIn(
            ("enabled", GLFixedFunctionCapability.LIGHTING, False),
            backend.calls,
        )

    def test_depth_state_applies_depth_not_blend(self):
        backend = RecordingBackend()
        depth = DepthState(test=False, write=False)

        depth.apply(
            state=type(
                "State",
                (),
                {
                    "backend": backend,
                    "set_enabled": lambda _self, cap, enabled: backend.calls.append(
                        ("enabled", cap, enabled)
                    ),
                },
            )()
        )

        call_names = [call[0] for call in backend.calls]
        self.assertIn("depth_test", call_names)
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
        self.assertIsInstance(backend.frame, GLFrameDriver)
        self.assertIsInstance(backend.raster, GLRasterDriver)
        self.assertIsInstance(backend.legacy, GLLegacyPipeline)

    def test_raster_driver_delegates_to_opengl(self):
        raster = GLRasterDriver()

        with (
            patch("picogl.backend.gl.driver.raster.glLineWidth") as line_width,
            patch("picogl.backend.gl.driver.raster.glPolygonMode") as polygon_mode,
            patch("picogl.backend.gl.driver.raster.glPointSize") as point_size,
            patch(
                "picogl.backend.gl.driver.raster.glGetFloatv",
                return_value=(1.0, 10.0),
            ) as get_float,
            patch("picogl.backend.gl.driver.raster.glPolygonOffset") as polygon_offset,
        ):
            raster.set_line_width(2.0)
            raster.set_polygon_mode(GLFace.FRONT_AND_BACK, GL_LINE)
            raster.set_point_size(3.0)
            raster.set_clamped_point_size(12.0)
            raster.set_polygon_offset(-1.0, -1.0)

        line_width.assert_called_once_with(2.0)
        polygon_mode.assert_called_once_with(GLFace.FRONT_AND_BACK, GL_LINE)
        self.assertEqual(point_size.call_args_list, [call(3.0), call(10.0)])
        get_float.assert_called_once()
        polygon_offset.assert_called_once_with(-1.0, -1.0)

    def test_raster_driver_caches_line_width(self):
        raster = GLRasterDriver()

        with patch("picogl.backend.gl.driver.raster.glLineWidth") as line_width:
            raster.set_line_width(2.0)
            raster.set_line_width(2.0)

        line_width.assert_called_once_with(2.0)

    def test_raster_driver_get_line_width_uses_cache(self):
        raster = GLRasterDriver()

        with (
            patch("picogl.backend.gl.driver.raster.glLineWidth"),
            patch("picogl.backend.gl.driver.raster.glGetFloatv") as get_float,
        ):
            raster.set_line_width(2.5)
            self.assertEqual(raster.get_line_width(), 2.5)

        get_float.assert_not_called()

    def test_raster_driver_caches_polygon_mode(self):
        raster = GLRasterDriver()

        with patch("picogl.backend.gl.driver.raster.glPolygonMode") as polygon_mode:
            raster.set_polygon_mode(GLFace.FRONT_AND_BACK, GL_LINE)
            raster.set_polygon_mode(GLFace.FRONT_AND_BACK, GL_LINE)

        polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)

    def test_raster_shared_api_uses_singleton_cache(self):
        GLRasterDriver._shared = None
        shared = GLRasterDriver.shared()

        with patch("picogl.backend.gl.driver.raster.glLineWidth"):
            GLRasterDriver.shared().set_line_width(4.0)

        self.assertEqual(shared.get_line_width(), 4.0)

    def test_glbackend_owns_per_instance_raster_driver(self):
        GLRasterDriver._shared = None
        backend = GLBackend(binding=FakeBinding())

        with patch("picogl.backend.gl.driver.raster.glLineWidth"):
            backend.raster.set_line_width(4.0)

        self.assertIsNot(backend.raster, GLRasterDriver.shared())
        self.assertEqual(backend.raster.get_line_width(), 4.0)

    def test_raster_isolated_instance_does_not_use_shared(self):
        GLRasterDriver._shared = None
        shared = GLRasterDriver.shared()
        shared.set_line_width(1.0)

        isolated = GLRasterDriver()
        with patch("picogl.backend.gl.driver.raster.glLineWidth"):
            isolated.set_line_width(3.0)

        self.assertEqual(isolated.get_line_width(), 3.0)
        self.assertEqual(shared.get_line_width(), 1.0)

    def test_resolve_polygon_mode_args(self):
        self.assertEqual(
            resolve_polygon_mode_args(GL_LINE),
            (GLFace.FRONT_AND_BACK, GL_LINE),
        )
        self.assertEqual(
            resolve_polygon_mode_args(GLFace.FRONT, GL_LINE),
            (GLFace.FRONT, GL_LINE),
        )
        with self.assertRaises(TypeError):
            resolve_polygon_mode_args()

    def test_raster_driver_apply_raster_state(self):
        raster = GLRasterDriver()
        state = RasterState(line_width=2.5, polygon_mode=GLFillMode.LINE)

        with (
            patch("picogl.backend.gl.driver.raster.glLineWidth") as line_width,
            patch("picogl.backend.gl.driver.raster.glPolygonMode") as polygon_mode,
        ):
            raster.apply(state)
            raster.apply(state)

        line_width.assert_called_once_with(2.5)
        polygon_mode.assert_called_once_with(GL_FRONT_AND_BACK, GL_LINE)

    def test_state_subsystem_drivers_delegate_to_opengl(self):
        capabilities = GLCapabilityDriver()
        depth = GLDepthDriver(capabilities)
        blend = GLBlendDriver(capabilities)

        with (
            patch("picogl.backend.gl.driver.capability.gl_enable") as enable,
            patch("picogl.backend.gl.driver.capability.glDisable") as disable,
            patch(
                "picogl.backend.gl.driver.capability.glIsEnabled", return_value=True
            ) as is_enabled,
            patch("picogl.backend.gl.driver.depth.glDepthMask") as depth_mask,
            patch("picogl.backend.gl.driver.depth.glDepthFunc") as depth_func,
            patch("picogl.backend.gl.driver.blend.glBlendFunc") as blend_func,
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
            patch.object(
                backend.capabilities, "is_enabled", return_value=True
            ) as is_enabled,
            patch.object(backend.capabilities, "set_enabled") as set_enabled,
            patch.object(backend.depth, "set_depth_test") as set_depth_test,
            patch.object(backend.depth, "set_depth_write") as set_depth_write,
            patch.object(backend.depth, "set_depth_func_gl_less") as set_depth_func,
            patch.object(backend.blend, "set_blend") as set_blend,
            patch.object(backend.blend, "set_blend_func") as set_blend_func,
            patch.object(backend.blend, "setup_blending") as setup_blending,
        ):
            backend.capabilities.enable(GL_CULL_FACE)
            backend.capabilities.disable(GL_LIGHTING)
            self.assertTrue(backend.capabilities.is_enabled(GL_DEPTH_TEST))
            backend.depth.set_depth_test(True)
            backend.depth.set_depth_write(False)
            backend.depth.set_depth_func_gl_less()
            backend.blend.set_blend(True)
            backend.blend.set_blend_func(GL_ONE, GL_ZERO)
            backend.blend.set_alpha_blending()
            backend.capabilities.set_enabled(GLPipelineCapability.CULL_FACE, True)
            backend.capabilities.set_enabled(GLFixedFunctionCapability.LIGHTING, False)

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
            [
                call(GLPipelineCapability.CULL_FACE, True),
                call(GLFixedFunctionCapability.LIGHTING, False),
            ],
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
            backend.raster.set_line_width(2.0)
            gl_set_polygon_mode(GLFace.FRONT_AND_BACK, GL_LINE)
            backend.raster.set_point_size(3.0)
            backend.raster.set_clamped_point_size(4.0)
            backend.raster.set_polygon_offset(-1.0, -1.0)

        set_line_width.assert_called_once_with(2.0)
        set_polygon_mode.assert_called_once_with(GLFace.FRONT_AND_BACK, GL_LINE)
        set_point_size.assert_called_once_with(3.0)
        set_clamped_point_size.assert_called_once_with(4.0)
        set_polygon_offset.assert_called_once_with(-1.0, -1.0)

    def test_legacy_pipeline_delegates_to_opengl(self):
        legacy = GLLegacyPipeline()
        material = PhongMaterial(
            ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
            diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
            specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch(
                "picogl.backend.legacy.core.camera.projection_state.gl_matrix_mode"
            ) as matrix_mode,
            patch(
                "picogl.backend.legacy.core.camera.projection_state.gl_load_identity"
            ) as load_identity,
            patch(
                "picogl.backend.legacy.core.camera.projection_state.glu_perspective"
            ) as perspective,
            patch("picogl.backend.legacy.core.pipeline.gl_translatef") as translate,
            patch("picogl.backend.legacy.core.pipeline.gl_light_fv") as lightfv,
            patch("picogl.backend.legacy.core.pipeline.gl_material_fv") as materialfv,
            patch("picogl.backend.legacy.core.pipeline.gl_material_f") as materialf,
        ):
            legacy.set_projection(45.0, 1.5, 0.1, 1000.0)
            legacy.translate(1, 2, 3)
            legacy.set_light([0.0, 0.0, 10.0, 1.0])
            legacy.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        self.assertEqual(
            matrix_mode.call_args_list,
            [
                call(GLLegacyMatrixMode.PROJECTION),
                call(GLLegacyMatrixMode.MODELVIEW),
            ],
        )
        load_identity.assert_called_once_with()
        perspective.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)
        translate.assert_called_once_with(1.0, 2.0, 3.0)
        lightfv.assert_called_once_with(
            light=GL_LIGHT0,
            param=GLLightParameter.POSITION,
            position=[0.0, 0.0, 10.0, 1.0],
        )
        self.assertEqual(
            materialfv.call_args_list,
            [
                call(
                    GLFace.FRONT_AND_BACK,
                    GLLightParameter.AMBIENT,
                    material.ambient.to_tuple(),
                ),
                call(
                    GLFace.FRONT_AND_BACK,
                    GLLightParameter.DIFFUSE,
                    material.diffuse.to_tuple(),
                ),
                call(
                    GLFace.FRONT_AND_BACK,
                    GLLightParameter.SPECULAR,
                    material.specular.to_tuple(),
                ),
            ],
        )
        materialf.assert_called_once_with(
            GLFace.FRONT_AND_BACK,
            GL_SHININESS,
            material.shininess,
        )

    def test_glbackend_fixed_function_uses_legacy_pipeline(self):
        backend = GLBackend(binding=FakeBinding())
        material = PhongMaterial(
            ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
            diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
            specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch.object(backend.legacy, "set_projection") as set_projection,
            patch.object(backend.legacy, "translate") as translate,
            patch.object(backend.legacy, "set_light") as set_light,
            patch.object(backend.legacy, "set_material") as set_material,
        ):
            backend.legacy.set_projection(45.0, 1.5, 0.1, 1000.0)
            backend.legacy.translate(1, 2, 3)
            backend.legacy.set_light([0.0, 0.0, 10.0, 1.0])
            backend.legacy.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        set_projection.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)
        translate.assert_called_once_with(1, 2, 3)
        set_light.assert_called_once_with(
            [0.0, 0.0, 10.0, 1.0],
        )
        set_material.assert_called_once_with(GLMaterialFace.FRONT_AND_BACK, material)

    def test_geometry_driver_delegates_to_binding_and_draw_elements(self):
        binding = RecordingBinding()
        geometry = GLGeometryDriver(binding)
        mesh = object()

        with (
            patch(
                "picogl.backend.gl.driver.geometry.gl_draw_elements"
            ) as draw_elements,
            patch("picogl.backend.gl.driver.geometry.gl_draw_arrays") as draw_arrays,
            patch("picogl.backend.gl.driver.geometry.glBindVertexArray") as bind_vao,
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
            patch("picogl.backend.gl.driver.texture.gl_bind_texture") as bind_texture,
            patch(
                "picogl.backend.gl.driver.texture.glDeleteTextures"
            ) as delete_textures,
        ):
            handle = textures.create_texture(4, 5, data=None)
            textures.bind_texture(7)
            textures.delete_texture(7)

        self.assertEqual(handle, 42)
        self.assertEqual(
            [call[0] for call in driver.calls], ["create", "bind", "initialize"]
        )
        self.assertEqual(driver.calls[0][1].spec.width, 4)
        self.assertEqual(driver.calls[0][1].spec.height, 5)
        bind_texture.assert_called_once_with(GL_TEXTURE_2D, 7)
        delete_textures.assert_called_once_with([7])

    def test_legacy_attribute_binder_delegates_to_client_state_calls(self):
        binder = LegacyAttributeBinder()
        data = object()

        with (
            patch(
                "picogl.wrappers.client_state.gl_enable_legacy_client_state"
            ) as enable_client,
            patch("picogl.wrappers.pointer.gl_vertex_array_pointer") as vertex_pointer,
            patch("picogl.wrappers.pointer.gl_normal_array_pointer") as normal_pointer,
            patch("picogl.wrappers.pointer.gl_color_array_pointer") as color_pointer,
            patch(
                "picogl.wrappers.pointer.gl_texcoord_array_pointer"
            ) as texcoord_pointer,
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
                call(GLClientState.VERTEX),
                call(GLClientState.NORMAL),
                call(GLClientState.COLOR),
                call(GLClientState.TEXCOORD),
            ],
        )
        vertex_pointer.assert_called_once_with(
            pointer=data, size=3, num_type=GL_FLOAT, stride=0
        )
        normal_pointer.assert_called_once_with(
            pointer=data, num_type=GL_FLOAT, stride=0
        )
        color_pointer.assert_called_once_with(
            pointer=data, size=4, num_type=GL_FLOAT, stride=0
        )
        texcoord_pointer.assert_called_once_with(
            pointer=data, size=2, num_type=GL_FLOAT, stride=0
        )

    def test_glbackend_geometry_texture_facades_and_attribute_subsystem(self):
        backend = GLBackend(binding=FakeBinding())
        mesh = object()
        data = object()

        with (
            patch.object(backend.geometry, "draw_mesh") as draw_mesh,
            patch.object(backend.geometry, "draw_elements") as draw_elements,
            patch.object(
                backend.geometry, "draw_bound_elements"
            ) as draw_bound_elements,
            patch.object(backend.geometry, "draw_arrays") as draw_arrays,
            patch.object(
                backend.geometry,
                "draw_arrays_bound_vao",
            ) as draw_arrays_bound_vao,
            patch.object(
                backend.textures, "create_texture", return_value=9
            ) as create_texture,
            patch.object(backend.textures, "bind_texture") as bind_texture,
            patch.object(backend.textures, "delete_texture") as delete_texture,
            patch.object(
                backend.attributes, "enable_vertex_array"
            ) as enable_vertex_array,
            patch.object(
                backend.attributes, "set_vertex_pointer"
            ) as set_vertex_pointer,
            patch.object(
                backend.attributes, "enable_normal_array"
            ) as enable_normal_array,
            patch.object(
                backend.attributes, "set_normal_pointer"
            ) as set_normal_pointer,
            patch.object(
                backend.attributes, "enable_color_array"
            ) as enable_color_array,
            patch.object(backend.attributes, "set_color_pointer") as set_color_pointer,
            patch.object(
                backend.attributes, "enable_texcoord_array"
            ) as enable_texcoord_array,
            patch.object(
                backend.attributes, "set_texcoord_pointer"
            ) as set_texcoord_pointer,
        ):
            backend.geometry.draw_mesh(mesh, GL_LINE)
            backend.geometry.draw_elements(GL_LINE, [0, 1, 2])
            backend.geometry.draw_bound_elements(GL_LINE, 4, GL_UNSIGNED_INT, None)
            backend.geometry.draw_arrays(GL_LINE, 1, 6)
            backend.geometry.draw_arrays_bound_vao(9, GL_LINE, 2, 7)
            self.assertEqual(backend.textures.create_texture(4, 5, None), 9)
            backend.textures.bind_texture(7)
            backend.textures.delete_texture(7)
            backend.attributes.enable_vertex_array()
            backend.attributes.set_vertex_pointer(data)
            backend.attributes.enable_normal_array()
            backend.attributes.set_normal_pointer(data)
            backend.attributes.enable_color_array()
            backend.attributes.set_color_pointer(data, 4)
            backend.attributes.enable_texcoord_array()
            backend.attributes.set_texcoord_pointer(data)

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
            patch("picogl.backend.gl.driver.frame.gl_viewport") as viewport,
            patch(
                "picogl.backend.legacy.core.pipeline.glLoadIdentity"
            ) as load_identity,
            patch("picogl.backend.legacy.core.pipeline.glTranslatef") as translate,
            patch("picogl.backend.legacy.core.pipeline.glLightfv") as lightfv,
            patch("picogl.backend.gl.driver.frame.glClearColor") as clear_color,
        ):
            backend.frame.set_viewport(Viewport(1, 2, 3, 4))
            backend.legacy.load_identity()
            backend.legacy.translate(1, 2, 3)
            backend.legacy.set_light([0.0, 0.0, 10.0, 1.0])
            backend.frame.set_clear_color((0.1, 0.2, 0.3, 1.0))

        viewport.assert_called_once_with(1, 2, 3, 4)
        load_identity.assert_called_once_with()
        translate.assert_called_once_with(1.0, 2.0, 3.0)
        lightfv.assert_called_once_with(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
        clear_color.assert_called_once_with(0.1, 0.2, 0.3, 1.0)

    def test_glbackend_applies_clip_state(self):
        backend = GLBackend(binding=FakeBinding())
        clip = GLClipPlaneState(enabled0=True, enabled1=False)

        with patch.object(clip, "apply") as apply:
            backend.clip.apply(clip)

        self.assertIs(backend.clip, clip)
        apply.assert_called_once_with(backend.state_manager)

    def test_glbackend_applies_stored_clip_state(self):
        backend = GLBackend(binding=FakeBinding())

        with patch.object(backend.clip, "apply") as apply:
            backend.apply_clip_state()

        apply.assert_called_once_with(backend.state_manager)

    def test_glbackend_perspective_projection_delegates_to_opengl(self):
        backend = GLBackend(binding=FakeBinding())

        with (
            patch(
                "picogl.backend.legacy.core.camera.projection_state.gl_matrix_mode"
            ) as matrix_mode,
            patch(
                "picogl.backend.legacy.core.camera.projection_state.gl_load_identity"
            ) as load_identity,
            patch(
                "picogl.backend.legacy.core.camera.projection_state.glu_perspective"
            ) as perspective,
        ):
            backend.legacy.set_projection(45.0, 1.5, 0.1, 1000.0)

        self.assertEqual(
            matrix_mode.call_args_list,
            [
                call(GLLegacyMatrixMode.PROJECTION),
                call(GLLegacyMatrixMode.MODELVIEW),
            ],
        )
        load_identity.assert_called_once_with()
        perspective.assert_called_once_with(45.0, 1.5, 0.1, 1000.0)

    def test_glbackend_set_material_delegates_to_opengl(self):
        backend = GLBackend(binding=FakeBinding())
        material = PhongMaterial(
            ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
            diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
            specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
            shininess=32.0,
        )

        with (
            patch("picogl.backend.legacy.core.pipeline.gl_material_fv") as materialfv,
            patch("picogl.backend.legacy.core.pipeline.gl_material_f") as materialf,
        ):
            backend.legacy.set_material(GLMaterialFace.FRONT_AND_BACK, material)

        self.assertEqual(
            materialfv.call_args_list,
            [
                call(
                    GLFace.FRONT_AND_BACK,
                    GL_AMBIENT,
                    material.ambient.to_tuple(),
                ),
                call(
                    GLFace.FRONT_AND_BACK,
                    GL_DIFFUSE,
                    material.diffuse.to_tuple(),
                ),
                call(
                    GLFace.FRONT_AND_BACK,
                    GL_SPECULAR,
                    material.specular.to_tuple(),
                ),
            ],
        )
        materialf.assert_called_once_with(
            GLFace.FRONT_AND_BACK,
            GL_SHININESS,
            material.shininess,
        )


if __name__ == "__main__":
    unittest.main()
