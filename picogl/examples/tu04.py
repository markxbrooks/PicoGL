# import os,sys
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from decologr import Decologr as log
from OpenGL.GL import *  # pylint: disable=W0614
from picogl.backend.gl.api import gl_bind_texture, gl_get_active_texture0
from picogl.backend.gl.api.glm import glm_identity_matrix
from picogl.backend.modern.core.shader.files import ShaderFiles
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.core.uniform import gl_uniform1i
# from picogl.gpu.buffers.vertex import data
from picogl.ui.backend.glut.window.glut import GlutRendererWindow
from picogl.utils.loader.texture import TextureLoader
from pyglm import glm

# from utils.objLoader import objLoader
# from utils.textureLoader import textureLoader


class MeshUE4:

    def __init__(self):
        self.tangent_xz = None
        self.texcoords = None
        self.vertices = None
        self.indices = None

    def load_mesh(self):
        from ue4reader import uasset

        ArchiveName = "D:/unpack/objects/Weapon/Rifles/AK-47/Meshes/AK-47_01.uasset"
        # ArchiveName = "D:/unpack/objects/Weapon/Rifles/AWM/Meshes/AWM_01.uasset"
        asset = uasset.UAssetReader(ArchiveName, forceUE4Ver=513)
        mesh_obj = asset.ExportsMap[1].GetObject()
        mesh_obj.Serialize(asset)
        mesh_obj.properties[1].to_dict()
        return mesh_obj.RenderData.LODResources[0]

    def getMesh(self):
        ue4LOD = self.load_mesh()
        self.vertices = vertex_data.VertexData.to_array()
        self.indices = ue4LOD.IndexBuffer.to_array()
        self.texcoords = (
            ue4LOD.VertexBuffers.StaticMeshVertexBuffer.TexcoordData.to_array()
        )
        self.tangent_xz = (
            ue4LOD.VertexBuffers.StaticMeshVertexBuffer.TangentsData.to_array()
        )
        # self.texcoords= []
        # for i in range(0,len(self._texcoords),2):
        # 	print "."
        # 	self.texcoords.append(float(self._texcoords[i]))
        # 	self.texcoords.append(1.0 - float(self._texcoords[i+1]))
        return self


def bind_active_texture0():
    """bind active texture (0)"""
    gl_get_active_texture0()
    gl_bind_texture(target=GL_TEXTURE_2D, tex_id=self.context.texture_buffer)
    gl_uniform1i(
        self.context.texture_id, 0
    )  # // Set  "myTextureSampler" sampler to use Texture Unit 0


class Tu01Win(GlutRendererWindow):
    class GLContext(object):
        pass

    def __init__(
        self,
        width,
        height,
        title: str = None,
        context: GLContext = None,
        *args,
        **kwargs,
    ):
        super().__init__(width, height, title, context, args, kwargs)
        self.shader = None

    def initializeGL(self):
        glClearColor(0.0, 0, 0.4, 0)
        glDepthFunc(GL_LESS)
        gl_enable(GL_DEPTH_TEST)
        gl_enable(GL_CULL_FACE)

    def keyPressEvent(self, key, x, y):
        pass

    def mousePressEvent(self, *args, **kwargs):
        pass

    def mouseMoveEvent(self, *args, **kwargs):
        pass

    def initialize(self):
        self.context = self.GLContext()

        self.shader = shader = ShaderProgram()
        shader_files = ShaderFiles(
            vertex="vertex.glsl", fragment="fragment.glsl", glsl_dir="glsl/tu02"
        )

        shader.compiler.compile_shader_files(shader_files)
        # shader var ids
        self.context.mvp_id = glGetUniformLocation(shader.program, "mvp_matrix")
        self.context.texture_id = glGetUniformLocation(
            shader.program, "myTextureSampler"
        )

        texture = TextureLoader("resources/tu05/AK-47_01_D_Fix.png")
        self.context.texture_buffer = texture.texture_gl_id

        model = MeshUE4().getMesh()
        self.context.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.context.vertex_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            len(model.vertices) * 4,
            (GLfloat * len(model.vertices))(*model.vertices),
            GL_STATIC_DRAW,
        )

        self.context.uv_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.context.uv_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            len(model.texcoords) * 4,
            (GLfloat * len(model.texcoords))(*model.texcoords),
            GL_STATIC_DRAW,
        )

        self.context.indices = glGenBuffers(1)
        self.context.indices_size = len(model.indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.context.indices)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            len(model.indices) * 2,
            (GLushort * len(model.indices))(*model.indices),
            GL_STATIC_DRAW,
        )

    def calc_mvp(self, width=1920, height=1080):
        self.context.projection_matrix = glm.perspective(
            glm.radians(45.0), float(width) / float(height), 0.1, 1000.0
        )
        self.context.View = glm.lookAt(
            glm.vec3(80, 80, 80),  # Camera is at (4,3,-3), in World Space
            glm.vec3(0, 0, 0),  # and looks at the (0.0.0))
            glm.vec3(0, 1, 0),
        )  # Head is up (set to 0,-1,0 to look upside-down)

        self.context.model_matrix = glm_identity_matrix()
        # print self.context.model_matrix
        self.context.mvp_matrix = (
            self.context.projection_matrix
            * self.context.view_matrix
            * self.context.model_matrix
        )

    def resizeGL(self, width, height):
        """resizeGL"""
        log.message("resizetGL")
        glViewport(0, 0, width, height)
        self.calc_mvp(width, height)

    def paintGL(self):
        """paintGL"""
        log.message("paintGL")
        # print self.context.mvp_matrix
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.begin()
        glUniformMatrix4fv(
            self.context.mvp_id, 1, GL_FALSE, glm.value_ptr(self.context.mvp_matrix)
        )

        bind_active_texture0()

        gl_enableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        gl_enableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.context.uv_buffer)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.context.indices)

        glDrawElements(
            GL_TRIANGLES,  # mode
            self.context.indices_size,  # // count
            GL_UNSIGNED_SHORT,  # // type
            None,  # // element array buffer offset
        )

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        self.shader.end()


if __name__ == "__main__":
    win = Tu01Win(width=400, height=300)
    win.initializeGL()
    win.initialize()
    win.run()
