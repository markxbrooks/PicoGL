"""Tests for typed fixed-function light and material value objects."""

from unittest.mock import call, patch

from picogl.backend.gl.capability import GLFixedFunctionCapability, GLMaterialFace
from picogl.backend.gl.legacy.lighting import DEFAULT_LEGACY_LIGHT, gl_legacy_lighting
from picogl.backend.gl.lighting import (
    EYE_SPACE_LIGHTING,
    SECONDARY_LIGHTS,
    LightSource,
    apply_light,
    set_secondary_lights,
)
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import GLLightParameter
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


def test_apply_light_converts_value_objects_to_tuples():
    light = LightSource(
        position=Vec4(1.0, 2.0, 3.0, 0.0),
        ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
        diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
        specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
    )

    with patch("picogl.backend.gl.lighting.driver.GLLightSource.lightf") as lightf:
        apply_light(GLFixedFunctionCapability.LIGHT0, light)

    assert lightf.call_args_list == [
        call(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.POSITION,
            light.position.to_tuple(),
        ),
        call(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.AMBIENT,
            light.ambient.to_tuple(),
        ),
        call(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.DIFFUSE,
            light.diffuse.to_tuple(),
        ),
        call(
            GLFixedFunctionCapability.LIGHT0,
            GLLightParameter.SPECULAR,
            light.specular.to_tuple(),
        ),
    ]


def test_phong_material_apply_converts_value_objects_to_tuples():
    material = PhongMaterial(
        ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
        diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
        specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
        emission=RGBAColor(0.05, 0.06, 0.07, 1.0),
        shininess=32.0,
    )

    with (
        patch("picogl.backend.gl.phong.material.gl_material_fv") as material_fv,
        patch("picogl.backend.gl.phong.material.gl_material_f") as material_f,
    ):
        material.apply(GLMaterialFace.FRONT_AND_BACK)

    assert material_fv.call_args_list == [
        call(
            GLMaterialFace.FRONT_AND_BACK,
            GLLightParameter.AMBIENT,
            material.ambient.to_tuple(),
        ),
        call(
            GLMaterialFace.FRONT_AND_BACK,
            GLLightParameter.DIFFUSE,
            material.diffuse.to_tuple(),
        ),
        call(
            GLMaterialFace.FRONT_AND_BACK,
            GLLightParameter.SPECULAR,
            material.specular.to_tuple(),
        ),
        call(
            GLMaterialFace.FRONT_AND_BACK,
            GLLightParameter.EMISSION,
            material.emission.to_tuple(),
        ),
    ]
    material_f.assert_called_once_with(
        GLMaterialFace.FRONT_AND_BACK,
        GLLightParameter.SHININESS,
        material.shininess,
    )


def test_gl_legacy_lighting_applies_default_value_objects():
    with (
        patch("picogl.backend.gl.legacy.lighting.enable_light") as enable,
        patch.object(PhongMaterial, "apply") as apply_material,
    ):
        gl_legacy_lighting()

    enable.assert_called_once_with(
        GLFixedFunctionCapability.LIGHT0, DEFAULT_LEGACY_LIGHT
    )
    apply_material.assert_called_once_with(GLMaterialFace.FRONT_AND_BACK)


def test_eye_space_lighting_apply_enables_light0_and_shininess():
    with (
        patch("picogl.backend.gl.lighting.system.GLCapabilityDriver.enable") as enable,
        patch("picogl.backend.gl.lighting.system.gl_light_model_fv") as light_model,
        patch("picogl.backend.gl.lighting.system.enable_light") as enable_light,
        patch("picogl.backend.gl.lighting.system.gl_material_f") as material_f,
        patch("picogl.backend.gl.lighting.system.gl_pixel_store_i") as pixel_store,
    ):
        EYE_SPACE_LIGHTING.apply()

    enable.assert_called_once_with(GLFixedFunctionCapability.LIGHTING)
    light_model.assert_called_once()
    enable_light.assert_called_once()
    assert enable_light.call_args[0][0] == GLFixedFunctionCapability.LIGHT0
    material_f.assert_called_once()
    assert material_f.call_args[0][2] == 32.0
    pixel_store.assert_called_once()


def test_set_secondary_lights_enable_and_disable():
    with (
        patch("picogl.backend.gl.lighting.presets.enable_light") as enable,
        patch("picogl.backend.gl.lighting.presets.disable_light") as disable,
    ):
        set_secondary_lights(True)
        assert enable.call_count == len(SECONDARY_LIGHTS)
        set_secondary_lights(False)
        assert disable.call_count == len(SECONDARY_LIGHTS)
        assert set(c.args[0] for c in disable.call_args_list) == set(
            SECONDARY_LIGHTS.keys()
        )
