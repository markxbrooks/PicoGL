from typing import Optional

from decologr import Decologr as log
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLUT import *  # pylint: disable=W0614

from picogl.backend.gl.api.polygon_mode import gl_polygon_mode
from picogl.backend.gl.capability import GLMaterialFace
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.state.fill import GLFillMode
from picogl.backend.glm.glm import glm_identity_matrix
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.backend.modern.core.shader.mvp.controller import MVPController
from picogl.core.rgbcolor import RGBAColor
from picogl.examples.utils.world_sheet import WorldSheet
from picogl.ui.backend.glut.window.gl import GLWindow


class MeshViewWindow(GLWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = None
        self.meshes: Optional[list] = None
        self._mvp = None
        self.controller: MVPController = MVPController(self.update_if)

    def initializeGL(self):
        """initializeGL"""
        gl_initialize_background(RGBAColor(0.1, 0.1, 0.1, 0.8))

    def add_mesh(self, mesh_with_render: object):
        """add_mesh"""
        self.meshes.append(mesh_with_render.make_context())

    def init_context(self):
        """init_context"""
        self.meshes = []

    def calc_mvp(self, width: int = 0, height: int = 0):
        """calc_mvp"""
        if width != 0:
            self.controller.resize(width, height)
        self._mvp = self.controller.calc_mvp(glm_identity_matrix())

    def resizeGL(self, width, height):
        """resizeGL"""
        log.message("resizeGL")
        glViewport(0, 0, width, height)
        self.calc_mvp(width, height)

    def paintGL(self):
        """paintGL"""
        log.message("paintGL")
        self.calc_mvp()
        glClear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        for mesh in self.meshes:
            mesh.render(
                self._mvp,
                self.controller.view_matrix,
                self.controller.projection_matrix,
            )

    def processMenuEvents(self, *args, **kwargs):
        """processMenuEvents"""
        (action,) = args
        if action == 3:
            self.controller.reset()
            self.update_if()
        if action == 2:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
            self.update_if()
        if action == 4:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)
            self.update_if()
        return 0

    def init_default(self):
        """init_default"""
        self.controller = MVPController(self.update_if)
        self.initializeGL()
        self.init_context()
        self.add_mesh(WorldSheet(base_dir="."))
        self.menu = glutCreateMenu(self.processMenuEvents)
        glutAddMenuEntry("UV MAP", 1)
        glutAddMenuEntry("WireFrame Mode", 2)
        glutAddMenuEntry("GL_FILL Mode", 4)
        glutAddMenuEntry("Reset view", 3)
        glutAttachMenu(GLUT_RIGHT_BUTTON)
        return self
