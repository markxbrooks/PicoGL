"""
LegacyPipelineProtocol
"""

from typing import Any, Protocol, runtime_checkable

from picogl.core.rgbcolor import RGBAColor
from picogl.backend.gl.api.color import gl_color_4f, gl_color_material
from picogl.backend.gl.api.light import gl_light_fv
from picogl.backend.gl.api.material import gl_material_f, gl_material_fv
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.api.vertex.vertex_3f import gl_vertex_3f
from picogl.backend.gl.capability import FACE_MAP
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import (gl_load_identity,
                                                  gl_translatef)
from picogl.backend.gl.state.fill import (GLColorMaterialMode, GLFace, GLLight,
                                          GLLightParameter)
from picogl.backend.gl.state.texture import TexCoord2f, Vertex3f
from picogl.backend.glu.perspective import glu_perspective
from picogl.backend.state import gl_value
from picogl.texture.coord import gl_tex_coord2f


@runtime_checkable
class LegacyPipelineProtocol(Protocol):
    """Fixed-function and immediate-mode pipeline operations (legacy gl only)."""

    def set_matrix_mode_model_view(self): ...
    def set_matrix_mode_projection(self): ...
    def load_identity(self): ...
    def set_perspective(self, fovy, aspect, znear, zfar): ...
    def set_projection(self, fovy, aspect, znear, zfar): ...
    def translate(self, x, y, z): ...
    def set_light(self, position, light: Any = ...): ...
    def set_material(self, face, material): ...
    def set_color_material(
        self,
        face=...,
        mode=...,
    ): ...
    def set_color(self, rgba): ...
    def set_uniform_color(self, color, alpha): ...
    def tex_coord2f(self, coord: TexCoord2f): ...
    def vertex_3f(self, v1: Vertex3f): ...


class GLLegacyPipeline:
    """Fixed-function matrix, light, and material operations."""

    @staticmethod
    def set_matrix_mode_model_view():
        """
        Sets the current matrix mode to model-view.

        This function sets the current OpenGL matrix mode to model-view,
        allowing subsequent matrix operations to affect the model-view matrix.

        @return: None
        """
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    @staticmethod
    def set_matrix_mode_projection():
        """
        Sets the matrix mode to the default, which is the matrix mode
        """
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)

    @staticmethod
    def load_identity():
        """
        Provides a static method to reset the current OpenGL matrix to the identity matrix.

        This method is used to simplify transformations by resetting the matrix to a
        default state, which is the identity matrix. It interacts with the OpenGL
        graphic library to perform this operation.

        @return: None
        """
        gl_load_identity()

    @staticmethod
    def set_perspective(fovy: float, aspect: float, znear: float, zfar: float):
        """
        set perspective
        """
        glu_perspective(float(fovy), float(aspect), float(znear), float(zfar))

    @staticmethod
    def set_projection(fovy: float, aspect: float, znear: float, zfar: float):
        """
        set projection
        """
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        glu_perspective(float(fovy), float(aspect), float(znear), float(zfar))
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    @staticmethod
    def translate(x: float, y: float, z: float) -> None:
        """
        Translates the current coordinate system by the given x, y, and z amounts.

        This method applies a translation transformation to the current coordinate
        system. The parameters x, y, and z represent the translation distances along
        the respective axes.

        Args:
            x (float): The distance to translate along the x-axis.
            y (float): The distance to translate along the y-axis.
            z (float): The distance to translate along the z-axis.

        Returns:
            None
        """
        gl_translatef(float(x), float(y), float(z))

    @staticmethod
    def set_light(position, light: GLLight = GLLight.LIGHT0) -> None:
        """
        Sets the light source's position in the OpenGL context.

        Sets the specified light source's position based on the given parameters,
        allowing configuration of light sources within the OpenGL rendering
        pipeline.

        Args:
            position: The position of the light in 3D space, defined as a list
                or tuple of four float values (x, y, z, w coordinates).
            light: The specific light source to be set, defined as an instance
                of the GLLight enum. Defaults to GLLight.LIGHT0.

        Returns:
            None
        """
        gl_light_fv(
            light=gl_value(light), param=GLLightParameter.POSITION, position=position
        )

    @staticmethod
    def set_material(face, material: PhongMaterial) -> None:
        """
        Sets the material properties for a specified face using the provided PhongMaterial parameters.
        This method adjusts the ambient, diffuse, specular, and shininess values for the face
        in the OpenGL rendering context.

        Parameters:
            face: The specified face of the object to which the material properties are applied.
            material: An instance of PhongMaterial that encapsulates the ambient, diffuse,
                specular, and shininess properties to be set for the specified face.

        Returns:
            None
        """
        f = FACE_MAP.get(face, gl_value(face))
        gl_material_fv(f, GLLightParameter.AMBIENT, material.ambient.to_tuple())
        gl_material_fv(f, GLLightParameter.DIFFUSE, material.diffuse.to_tuple())
        gl_material_fv(f, GLLightParameter.SPECULAR, material.specular.to_tuple())
        gl_material_f(f, GLLightParameter.SHININESS, material.shininess)

    @staticmethod
    def set_color_material(
        face: GLFace = GLFace.FRONT_AND_BACK,
        mode: GLColorMaterialMode = GLColorMaterialMode.AMBIENT_AND_DIFFUSE,
    ) -> None:
        """
        Sets the color material mode for the specified face.

        This method sets the material property or combination of properties in the
        current OpenGL context to track the current color. The specified face and mode
        determine which material parameters will track the current color.

        Parameters:
            face (GLFace): Specifies which face(s) of the material to apply
                the color-material mode to. Default is GLFace.FRONT_AND_BACK.
            mode (GLColorMaterialMode): Specifies the color material mode
                to set. Default is GLColorMaterialMode.AMBIENT_AND_DIFFUSE.
        """
        f = FACE_MAP.get(face, gl_value(face))
        gl_color_material(f, gl_value(mode))

    @staticmethod
    def set_color(rgba: tuple[float, float, float, float]) -> None:
        """
        Sets the current drawing color for subsequent OpenGL rendering.

        This method sets the RGBA color using the provided tuple. Each of the four
        components in the tuple should range between 0.0 and 1.0. The color is applied
        to all OpenGL primitives that are drawn after calling this method.

        Parameters:
            rgba (tuple[float, float, float, float]): A tuple specifying the red, green,
                blue, and alpha components of the desired color. Each component must
                be a float within the range [0.0, 1.0].

        Returns:
            None
        """
        gl_color_4f(rgba)

    @staticmethod
    def set_rgba_color(rgba_color: RGBAColor) -> None:
        """
        Sets the RGBA color for the rendering pipeline.

        This method updates the color used in the rendering pipeline by providing
        a new RGBA color and passing it to the legacy OpenGL color setting function.

        Args:
            rgba_color (RGBAColor): A tuple or object representing RGBA color, where
            R, G, B, and A are values in the range [0, 1].

        Returns:
            None
        """
        GLLegacyPipeline.set_color(rgba_color.to_tuple())

    @staticmethod
    def tex_coord2f(coord: TexCoord2f) -> None:
        """
        Provides functionality to pass a 2-dimensional texture coordinate to the
        OpenGL rendering pipeline. This method is a static utility designed to
        make it convenient to set texture coordinates using a given TexCoord2f
        object.

        Parameters:
            coord (TexCoord2f): A data structure containing the `u` and `v`
                components of the 2D texture coordinate.

        Returns:
            None: This method does not return a value.

        Raises:
            Any exception raised by the underlying `gl_tex_coord2f` function call.
        """
        return gl_tex_coord2f(coord.u, coord.v)

    @staticmethod
    def vertex_3f(v1: Vertex3f):
        """
        Provides a static method to process a Vertex3f object and pass its
        coordinates to a corresponding OpenGL function.

        Methods
        -------
        vertex_3f(v1: Vertex3f)
            Accepts a Vertex3f object, extracts its x, y, and z coordinates,
            and sends them to the OpenGL gl_vertex_3f function.
        """
        gl_vertex_3f(v1.x, v1.y, v1.z)


# Preferred public name for fixed-function pipeline access.
LegacyPipeline = GLLegacyPipeline
