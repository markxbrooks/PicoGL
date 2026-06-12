from OpenGL.raw.GL.VERSION.GL_1_0 import (GL_COLOR_BUFFER_BIT,
                                          GL_DEPTH_BUFFER_BIT, glClear,
                                          glClearColor)


class GLFramebuffer:
    """GL Frame Buffer"""
    def __init__(self):
        self.color_attachments = []
        self.depth_attachment = None

    def bind(self):
        pass

    def clear(self, color=(0.0, 0.0, 0.0, 1.0)):
        glClearColor(*color)
        self.clear_background()

    def clear_background(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)