# PicoGL

**PicoGL** is a lightweight, Pythonic wrapper around Modern (and some Legacy) OpenGL — designed to make GPU programming simple, readable, and fun without sacrificing low-level control.

Whether you’re building interactive visualizations, scientific simulations, or games for fun, PicoGL gives you a clean, high-level API to work with shaders, buffers, and pipelines — while still letting you drop down to raw OpenGL when you need it.

---
![teapot](newell_teapot.PNG)


## ✨ Features

- **Modern OpenGL API** — Focus on shader-based rendering without legacy cruft.
- **Simple, Pythonic interface** — Write less boilerplate, get more done.
- **Full low-level access** — No “black box” abstractions; raw OpenGL calls available anytime.
- **Resource management** — Automatic cleanup of buffers, shaders, and textures.
- **Cross-platform** — Works anywhere Python and OpenGL do.

---

## 🚀 Installation

```bash
    git clone https://github.com/markxbrooks/PicoGL.git
    cd PicoGL
    pip install .
```
or for an editable version:

```bash
    pip install -e .
```
PyPi version coming soon!

## 📖 Documentation
In depth documentation can be found here, or in the Docs directory.
[https://github.com/markxbrooks/PicoGL/blob/main/doc/_build/picogl2.pdf]

##  Example usage to show a cube:
Found in the Examples directory, with mouse control

![cube](cube.png)

```python
"""Minimal PicoGL Cube. Compare to tu_01_color_cube.py"""

from pathlib import Path
from typing import NoReturn
from examples.data.cube_data import g_color_buffer_data, g_vertex_buffer_data
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow

GLSL_DIR = Path(__file__).parent / "glsl" / "tu01"


def main() -> NoReturn:
    """Set up the colored object dat and show it"""
    data = MeshData.from_raw(vertices=g_vertex_buffer_data, colors=g_color_buffer_data)
    render_window = RenderWindow(
        width=800, height=600, title="Cube window", data=data, glsl_dir=GLSL_DIR
    )
    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    main()

```
### With a corresponding renderer

```python
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_TRIANGLES

from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.renderer import GLContext, MeshData, RendererBase


class ObjectRenderer(RendererBase):
    """ Basic renderer class """

    def __init__(self,
                 context: GLContext,
                 data: MeshData,
                 glsl_dir: str):
        super().__init__()
        self.context, self.data = context, data
        self.glsl_dir = glsl_dir
        self.show_model = True

    def initialize_shaders(self):
        """Load and compile shaders."""
        self.context.create_shader_program(vertex_source_file="vertex.glsl",
                                           fragment_source_file="fragment.glsl",
                                           glsl_dir=self.glsl_dir)

    def initialize_buffers(self):
        """Create VAO and VBOs once."""
        if self.context.vaos is None:
            self.context.vaos = {}
        self.context.vaos["cube"] = cube_vao = VertexArrayObject()
        cube_vao.add_vbo(index=0, data=self.data.vbo, size=3)
        cube_vao.add_vbo(index=1, data=self.data.cbo, size=3)
        if self.data.nbo is not None:
            cube_vao.add_vbo(index=2, data=self.data.nbo, size=3)

    def render(self) -> None:
        """
        render dispatcher
        :return: None
        """
        if self.show_model:
            self._draw_model()
        # Add more conditions and corresponding draw functions as needed
        self._finalize_render()

    def _draw_model(self):
        """Draw the model_matrix"""
        cube_vao = self.context.vaos["cube"]
        shader = self.context.shader
        with shader, cube_vao:
            shader.uniform("mvp_matrix", self.context.mvp_matrix)
            shader.uniform("model_matrix", self.context.model_matrix)
            cube_vao.draw(mode=GL_TRIANGLES, index_count=self.data.vertex_count)

```
## Textured object
![texture](texture.PNG)

```python
"""
Demonstrating textures - compare to tu02_texture_without_normal.py
"""

from pathlib import Path
from typing import NoReturn

from examples import g_vertex_buffer_data, g_uv_buffer_data
from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.texture import TextureWindow

BASE_DIR = Path(__file__).resolve().parent
GLSL_DIR = BASE_DIR / "glsl" / "tu02"


def main() -> NoReturn:
    """Set up the cube and draw it with texture."""
    cube_data = MeshData.from_raw(vertices=g_vertex_buffer_data, uvs=g_uv_buffer_data)
    render_window = TextureWindow(
        width=800,
        height=600,
        title="texture window",
        data=cube_data,
        base_dir=BASE_DIR,
        glsl_dir=GLSL_DIR,
    )
    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    main()
```

## Teapot object
![teapot](newell_teapot.PNG)

```python
"""Minimal PicoGL Teapot."""

from pathlib import Path

from picogl.renderer import MeshData
from picogl.ui.backend.glut.window.object import RenderWindow
from picogl.utils.loader.object import ObjectLoader

GLSL_DIR = Path(__file__).parent / "glsl" / "teapot"


def main():
    """Set up the teapot object and show it."""
    object_file_name = "data/teapot.obj"
    obj_loader = ObjectLoader(object_file_name)
    teapot_data = obj_loader.to_array_style()
    data = MeshData.from_raw(
        vertices=teapot_data.vertices,
        normals=teapot_data.normals,
        colors=([[1.0, 0.0, 0.0]] * (len(teapot_data.vertices) // 3))
    )
    render_window = RenderWindow(
        width=800,
        height=600,
        title="Newell Teapot",
        glsl_dir=GLSL_DIR,
        data=data,
    )
    render_window.initialize()
    render_window.run()


if __name__ == "__main__":
    """Run the main function."""
    main()
```