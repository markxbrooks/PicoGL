from OpenGL.raw.GL.VERSION.GL_1_0 import glLightfv
from picogl.backend.gl.capability import GLFixedFunctionCapability
from picogl.backend.gl.state.fill import GLLightParameter


class GLLightSource:

    @staticmethod
    def lightf(
        light: GLFixedFunctionCapability,
        pname: GLLightParameter = GLLightParameter.DIFFUSE,
        params: list[float] = None,
    ):
        glLightfv(light, pname, params)
