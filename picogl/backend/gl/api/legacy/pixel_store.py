from OpenGL.raw.GL.VERSION.GL_1_0 import glPixelStorei


def gl_pixel_store_i(pname, param):
    glPixelStorei(pname, param)
