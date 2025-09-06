Quick Start Guide
=================

This guide will get you up and running with PicoGL in just a few minutes. We'll create a simple colored cube that you can rotate and interact with.

Prerequisites
-------------

Before starting, make sure you have:

* Python 3.7 or higher
* PicoGL installed (see :doc:`installation`)
* A system with OpenGL support

Your First PicoGL Program
-------------------------

Let's create a simple program that displays a colored cube:

.. code-block:: python

   from picogl.renderer import MeshData
   from picogl.ui.backend.glut.window.object import RenderWindow
   import numpy as np

   def main():
       # Define cube vertices (8 corners of a cube)
       vertices = np.array([
           # Front face
           [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1],
           # Back face
           [-1, -1, -1], [-1,  1, -1], [ 1,  1, -1], [ 1, -1, -1],
           # Top face
           [-1,  1, -1], [-1,  1,  1], [ 1,  1,  1], [ 1,  1, -1],
           # Bottom face
           [-1, -1, -1], [ 1, -1, -1], [ 1, -1,  1], [-1, -1,  1],
           # Right face
           [ 1, -1, -1], [ 1,  1, -1], [ 1,  1,  1], [ 1, -1,  1],
           # Left face
           [-1, -1, -1], [-1, -1,  1], [-1,  1,  1], [-1,  1, -1]
       ], dtype=np.float32)

       # Define colors for each vertex
       colors = np.array([
           # Front face (red)
           [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
           # Back face (green)
           [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0],
           # Top face (blue)
           [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
           # Bottom face (yellow)
           [1, 1, 0], [1, 1, 0], [1, 1, 0], [1, 1, 0],
           # Right face (magenta)
           [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1],
           # Left face (cyan)
           [0, 1, 1], [0, 1, 1], [0, 1, 1], [0, 1, 1]
       ], dtype=np.float32)

       # Create mesh data
       data = MeshData.from_raw(vertices=vertices, colors=colors)

       # Create render window
       window = RenderWindow(
           width=800,
           height=600,
           title="My First PicoGL Cube",
           data=data
       )

       # Initialize and run
       window.initialize()
       window.run()

   if __name__ == "__main__":
       main()

Save this code as ``my_first_cube.py`` and run it:

.. code-block:: bash

   python my_first_cube.py

You should see a window with a colorful cube that you can rotate with your mouse!

Understanding the Code
----------------------

Let's break down what this code does:

1. **Import PicoGL modules**:
   - ``MeshData``: Container for vertex and color data
   - ``RenderWindow``: Window for displaying 3D content

2. **Define vertices**: 24 vertices defining 6 faces of a cube
3. **Define colors**: One color per vertex
4. **Create mesh data**: Combine vertices and colors into a mesh
5. **Create window**: Set up the display window
6. **Run**: Start the interactive display

Key Concepts
------------

MeshData
~~~~~~~~

``MeshData`` is the core data structure in PicoGL. It holds all the information needed to render a 3D object:

.. code-block:: python

   data = MeshData.from_raw(
       vertices=vertices,    # 3D positions
       colors=colors,        # RGB colors
       normals=normals,      # Surface normals (optional)
       uvs=uvs              # Texture coordinates (optional)
   )

RenderWindow
~~~~~~~~~~~~

``RenderWindow`` provides the display interface. It handles:

* OpenGL context creation
* Window management
* User input (mouse, keyboard)
* Rendering loop

.. code-block:: python

   window = RenderWindow(
       width=800,           # Window width
       height=600,          # Window height
       title="My App",      # Window title
       data=mesh_data       # Mesh to display
   )

Interactive Controls
--------------------

The default controls are:

* **Mouse drag**: Rotate the view
* **Mouse wheel**: Zoom in/out
* **R key**: Reset rotation
* **W key**: Toggle wireframe mode
* **ESC key**: Exit

Adding More Features
--------------------

Textures
~~~~~~~~

To add textures to your cube:

.. code-block:: python

   # Load texture data
   from picogl.utils.loader.texture import TextureLoader
   
   texture_loader = TextureLoader("path/to/texture.png")
   texture = texture_loader.load()
   
   # Create mesh with UV coordinates
   data = MeshData.from_raw(
       vertices=vertices,
       colors=colors,
       uvs=uv_coordinates  # Texture coordinates
   )
   
   # Create textured render window
   window = TextureWindow(
       width=800,
       height=600,
       title="Textured Cube",
       data=data,
       use_texture=True,
       texture_file="texture.png"
   )

Lighting
~~~~~~~~

To add lighting effects:

.. code-block:: python

   # Create mesh with normals
   data = MeshData.from_raw(
       vertices=vertices,
       colors=colors,
       normals=normals  # Surface normals for lighting
   )

Multiple Objects
~~~~~~~~~~~~~~~~

To render multiple objects:

.. code-block:: python

   # Create multiple mesh data objects
   cube_data = MeshData.from_raw(vertices=cube_vertices, colors=cube_colors)
   sphere_data = MeshData.from_raw(vertices=sphere_vertices, colors=sphere_colors)
   
   # Create separate renderers for each object
   cube_renderer = ObjectRenderer(context=context, data=cube_data)
   sphere_renderer = ObjectRenderer(context=context, data=sphere_data)

Legacy Compatibility
--------------------

If you're having issues with modern OpenGL, try the legacy examples:

.. code-block:: python

   # Use legacy cube renderer
   from examples.legacy_cube_minimal import MinimalCubeRenderer
   
   renderer = MinimalCubeRenderer(width=800, height=600)
   renderer.run()

Common Issues
-------------

**Black screen or no rendering**
   - Check if OpenGL is supported on your system
   - Try the legacy examples for better compatibility

**Import errors**
   - Make sure PicoGL is installed: ``pip install picogl``
   - Check that all dependencies are installed

**Window doesn't appear**
   - Run from Terminal.app (macOS) or command prompt (Windows)
   - Check display environment variables

**Performance issues**
   - Reduce the number of vertices
   - Use simpler shaders
   - Try the legacy rendering mode

Next Steps
----------

Now that you have a basic understanding of PicoGL:

1. **Explore the examples** in the ``examples/`` directory
2. **Read the API documentation** to learn about all available classes
3. **Try the legacy examples** if you have compatibility issues
4. **Check out the molecular visualization examples** for more complex use cases

Examples to Try
---------------

* ``examples/cube.py`` - Basic colored cube
* ``examples/teapot.py`` - 3D teapot model
* ``examples/legacy_cube_minimal.py`` - Legacy-compatible cube
* ``examples/molecular_viewer.py`` - Molecular visualization

For more advanced examples, see the :doc:`examples` section.

Troubleshooting
---------------

If you run into problems:

1. **Check the installation guide** for platform-specific issues
2. **Try the legacy examples** for better compatibility
3. **Check the troubleshooting guide** for common solutions
4. **Report issues** on GitHub with system information

Happy coding with PicoGL! 🎉
