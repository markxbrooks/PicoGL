from OpenGL import GL as gl


def printOpenGLError():
    err = gl.glGetError()  # pylint: disable=E1111
    if err != gl.GL_NO_ERROR:
        print("GLERROR: ", gl.gluErrorString(err))  # pylint: disable=E1101


import os


# sys.path.append(os.path.abspath(os.path.dirname(__file__)))
class Shader(object):
    def initShaderFromGLSL(self, vertex_shader_paths, fragment_shader_paths):
        vertex_shader_source_list = []
        fragment_shader_source_list = []
        if isinstance(vertex_shader_paths, list):
            for GLSL in vertex_shader_paths:
                absDIR = os.path.abspath(
                    os.path.join(os.path.join(os.path.dirname(__file__), ".."), GLSL)
                )
                f = open(absDIR, "rb")
                vertex_shader_source_list.append(f.read())
                f.close()
            for GLSL in fragment_shader_paths:
                absDIR = os.path.abspath(
                    os.path.join(os.path.join(os.path.dirname(__file__), ".."), GLSL)
                )
                f = open(absDIR, "rb")
                fragment_shader_source_list.append(f.read())
                f.close()
            self.initShader(vertex_shader_source_list, fragment_shader_source_list)

    def initShader(self, vertex_shader_source_list, fragment_shader_source_list):
        # create program
        self.program = gl.glCreateProgram()  # pylint: disable=E1111
        # print('create program ',self.program)
        printOpenGLError()

        # vertex shader
        # print('compile vertex shader...')
        self.vertex_shader = gl.glCreateShader(
            gl.GL_VERTEX_SHADER
        )  # pylint: disable=E1111
        gl.glShaderSource(self.vertex_shader, vertex_shader_source_list)
        gl.glCompileShader(self.vertex_shader)
        if gl.GL_TRUE != gl.glGetShaderiv(self.vertex_shader, gl.GL_COMPILE_STATUS):
            err = gl.glGetShaderInfoLog(self.vertex_shader)
            raise Exception(err)
        gl.glAttachShader(self.program, self.vertex_shader)
        printOpenGLError()

        # fragment shader
        # print('compile fragment shader...')
        self.fragment_shader = gl.glCreateShader(
            gl.GL_FRAGMENT_SHADER
        )  # pylint: disable=E1111
        gl.glShaderSource(self.fragment_shader, fragment_shader_source_list)
        gl.glCompileShader(self.fragment_shader)
        if gl.GL_TRUE != gl.glGetShaderiv(self.fragment_shader, gl.GL_COMPILE_STATUS):
            err = gl.glGetShaderInfoLog(self.fragment_shader)
            raise Exception(err)
        gl.glAttachShader(self.program, self.fragment_shader)
        printOpenGLError()

        # print('link...')
        gl.glLinkProgram(self.program)
        if gl.GL_TRUE != gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS):
            err = gl.glGetShaderInfoLog(self.vertex_shader)
            raise Exception(err)
        printOpenGLError()

    def begin(self):
        if gl.glUseProgram(self.program):
            printOpenGLError()

    def end(self):
        gl.glUseProgram(0)
