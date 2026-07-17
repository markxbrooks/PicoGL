"""Tests for typed fixed-function light and material value objects."""

from unittest.mock import call, patch

from picogl.backend.gl.capability import (GLFixedFunctionCapability,
                                          GLMaterialFace)
from picogl.backend.gl.legacy.lighting import gl_legacy_lighting
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import GLLightParameter
from picogl.backend.legacy.core.camera.lighting import GLLight
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4


def test_gl_light_apply_converts_value_objects_to_tuples():
    light = GLLight(
        position=Vec4(1.0, 2.0, 3.0, 0.0),
        ambient=RGBAColor(0.1, 0.2, 0.3, 1.0),
        diffuse=RGBAColor(0.4, 0.5, 0.6, 1.0),
        specular=RGBAColor(0.7, 0.8, 0.9, 1.0),
    )

    with patch(
        "picogl.backend.legacy.core.camera.lighting.GLLightSource.lightf"
    ) as lightf:
        light.apply(GLFixedFunctionCapability.LIGHT0)

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
        patch.object(GLLight, "apply") as apply_light,
        patch.object(PhongMaterial, "apply") as apply_material,
    ):
        gl_legacy_lighting()

    apply_light.assert_called_once_with(GLFixedFunctionCapability.LIGHT0)
    apply_material.assert_called_once_with(GLMaterialFace.FRONT_AND_BACK)
