

from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLUT import *  # pylint: disable=W0614
from pyglm import glm

from examples.utils.world_sheet import WorldSheet
from picogl.backend.modern.core.shader.mvp.controller import MVPController
from picogl.ui.backend.glut.window.gl import GLWindow
from picogl.logger import Logger as log


class MeshViewWindow(GLWindow):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.menu = None
        self.meshes: Optional[list] = None
        self._mvp = None
        self.controller: MVPController = MVPController(self.update_if)

    def initializeGL(self):
        """initializeGL"""
        glClearColor(0.1, 0.1, 0.1, 0.8)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

    def add_mesh(self, mesh_with_render: object):
        """add_mesh"""
        self.meshes.append(mesh_with_render.make_context())

    def init_context(self):
        """init_context"""
        self.meshes = []

    def calc_mvp(self, width: int = 0, height: int = 0):
        """calc_mvp"""
        if width!=0:
            self.controller.resize(width, height)
        self._mvp = self.controller.calc_mvp(glm.mat4(1.0))

    def resizeGL(self, width, height):
        """resizeGL"""
        log.message("resizeGL")
        glViewport(0, 0, width, height)
        self.calc_mvp(width, height)

    def paintGL(self):
        """paintGL"""
        log.message("paintGL")
        self.calc_mvp()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for mesh in self.meshes:
            mesh.render(self._mvp, self.controller.view_matrix, self.controller.projection_matrix)
            
    def processMenuEvents(self,*args,**kwargs):
        """processMenuEvents"""
        action, = args
        if action == 3:
            self.controller.reset()
            self.update_if() 
        if action == 2:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            self.update_if()
        if action == 4:
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
            self.update_if()        
        return 0

    def init_default(self):
        """init_default"""
        self.controller = MVPController(self.update_if)
        self.initializeGL()
        self.init_context()    
        self.add_mesh(WorldSheet(base_dir="."))
        self.menu = glutCreateMenu(self.processMenuEvents)
        glutAddMenuEntry("UV MAP",1)
        glutAddMenuEntry("WireFrame Mode",2)
        glutAddMenuEntry("GL_FILL Mode",4)
        glutAddMenuEntry("Reset view",3)
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        return self


