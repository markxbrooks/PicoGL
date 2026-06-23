from OpenGL.raw.GL.VERSION.GL_1_0 import glClearColor, glClear


def gl_clear_color(color: tuple[float, float, float, float]):
    glClearColor(*color)


def gl_clear(mask):
    glClear(mask)