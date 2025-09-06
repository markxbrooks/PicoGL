Examples
========

PicoGL comes with a comprehensive set of examples demonstrating various features and use cases. This section provides an overview of all available examples and how to run them.

Basic Examples
--------------

Cube Example
~~~~~~~~~~~~

**File**: ``examples/cube.py``

A simple colored cube demonstrating basic mesh rendering.

.. code-block:: python

   from picogl.renderer import MeshData
   from picogl.ui.backend.glut.window.object import RenderWindow
   from examples.data.cube_data import g_vertex_buffer_data, g_color_buffer_data

   data = MeshData.from_raw(vertices=g_vertex_buffer_data, colors=g_color_buffer_data)
   window = RenderWindow(width=800, height=600, title="Cube", data=data)
   window.initialize()
   window.run()

**Features**:
* 36 vertices forming 12 triangles
* Per-vertex coloring
* Interactive rotation and zoom
* Modern OpenGL 3.3+ shaders

**Run**:
.. code-block:: bash

   python examples/cube.py

Teapot Example
~~~~~~~~~~~~~~

**File**: ``examples/teapot.py``

A 3D teapot model with lighting and shading.

.. code-block:: python

   from picogl.renderer import MeshData
   from picogl.ui.backend.glut.window.object import RenderWindow
   from picogl.utils.loader.object import ObjectLoader

   # Load teapot data
   obj_loader = ObjectLoader("data/teapot.obj")
   teapot_data = obj_loader.to_array_style()
   
   data = MeshData.from_raw(
       vertices=teapot_data.vertices,
       normals=teapot_data.normals,
       colors=[[1.0, 0.0, 0.0]] * (len(teapot_data.vertices) // 3)
   )
   
   window = RenderWindow(width=800, height=600, title="Teapot", data=data)
   window.initialize()
   window.run()

**Features**:
* Loaded from OBJ file
* Surface normals for lighting
* Phong shading
* Interactive controls

**Run**:
.. code-block:: bash

   python examples/teapot.py

Legacy Examples
---------------

For systems with limited OpenGL support (older macOS, etc.), use the legacy examples:

Legacy Cube (Minimal)
~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_cube_minimal.py``

Maximum compatibility cube renderer using only PyOpenGL.

**Features**:
* OpenGL 1.x immediate mode
* No external dependencies beyond PyOpenGL
* Works on any system with basic OpenGL support
* Same visual appearance as modern version

**Run**:
.. code-block:: bash

   python examples/legacy_cube_minimal.py

Legacy Cube (Fixed)
~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_cube_fixed.py``

PicoGL-integrated legacy cube using LegacyGLMesh.

**Features**:
* OpenGL 1.x/2.x compatibility
* Uses PicoGL LegacyGLMesh
* Falls back to wireframe if mesh loading fails
* Better integration with PicoGL ecosystem

**Run**:
.. code-block:: bash

   python examples/legacy_cube_fixed.py

Legacy Teapot (Minimal)
~~~~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_teapot_minimal.py``

Maximum compatibility teapot using built-in OpenGL primitives.

**Features**:
* Uses ``glutSolidTeapot()`` built-in primitive
* No external files required
* Maximum compatibility
* Interactive controls

**Run**:
.. code-block:: bash

   python examples/legacy_teapot_minimal.py

Legacy Teapot (Fixed)
~~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_teapot_fixed.py``

PicoGL-integrated legacy teapot with OBJ file support.

**Features**:
* Loads teapot from OBJ file
* Uses LegacyGLMesh for rendering
* Falls back to wireframe teapot if OBJ loading fails
* Full PicoGL integration

**Run**:
.. code-block:: bash

   python examples/legacy_teapot_fixed.py

Advanced Examples
-----------------

Molecular Visualization
~~~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/molecular_viewer.py``

Complex molecular visualization with atom and bond rendering.

**Features**:
* PDB file loading
* Atom and bond rendering
* Multiple rendering modes
* Interactive controls
* Scientific visualization

**Run**:
.. code-block:: bash

   python examples/molecular_viewer.py

Texture Examples
~~~~~~~~~~~~~~~~

**File**: ``examples/texture.py``

Demonstrates texture mapping and UV coordinates.

**Features**:
* Texture loading from image files
* UV coordinate mapping
* Multiple texture formats
* Texture filtering and wrapping

**Run**:
.. code-block:: bash

   python examples/texture.py

Shader Examples
~~~~~~~~~~~~~~~

**Directory**: ``examples/glsl/``

Various shader examples demonstrating different rendering techniques:

* ``tu01/`` - Basic color cube
* ``tu02/`` - Texture mapping
* ``tu04/`` - Lighting and shading
* ``tu07/`` - Standard shading
* ``tu08/`` - Transparent shading
* ``tu09/`` - Text rendering
* ``tu10/`` - Normal mapping

**Run**:
.. code-block:: bash

   # Run specific shader example
   python examples/tu_01_color_cube.py
   python examples/tu_02_texture_without_normal.py
   python examples/tu_04_lighting.py

Utility Examples
----------------

Mesh Viewer
~~~~~~~~~~~

**File**: ``examples/utils/meshViewer.py``

Generic mesh viewer for OBJ files.

**Features**:
* Load any OBJ file
* Interactive viewing
* Multiple rendering modes
* Export capabilities

**Run**:
.. code-block:: bash

   python examples/utils/meshViewer.py path/to/model.obj

Test Window
~~~~~~~~~~~

**File**: ``examples/utils/test_window.py``

Simple test window for debugging.

**Features**:
* Basic OpenGL context testing
* Simple rendering
* Debug information
* Error reporting

**Run**:
.. code-block:: bash

   python examples/utils/test_window.py

Running Examples
----------------

Prerequisites
~~~~~~~~~~~~~

Before running examples, ensure you have:

1. **PicoGL installed** (see :doc:`installation`)
2. **Required dependencies**:
   - PyOpenGL
   - NumPy
   - PyGLM
   - Pillow (for texture examples)

3. **OpenGL support** on your system

Basic Usage
~~~~~~~~~~~

Most examples can be run directly:

.. code-block:: bash

   # Navigate to the examples directory
   cd examples
   
   # Run a basic example
   python cube.py
   
   # Run a legacy example
   python legacy_cube_minimal.py

Interactive Controls
~~~~~~~~~~~~~~~~~~~

Most examples support these controls:

* **Mouse drag**: Rotate the view
* **Mouse wheel**: Zoom in/out
* **R key**: Reset rotation
* **W key**: Toggle wireframe mode
* **F key**: Fill mode
* **ESC key**: Exit

Some examples have additional controls:

* **N key**: Toggle normals display
* **Space**: Toggle auto-rotation
* **+/-**: Zoom in/out

Troubleshooting Examples
------------------------

Common Issues
~~~~~~~~~~~~~

**"No OpenGL context" error**
   - Try legacy examples instead
   - Run from Terminal.app (macOS) or command prompt (Windows)
   - Check display environment

**"Shader compilation failed" error**
   - Use legacy examples (no shaders required)
   - Check OpenGL version support
   - Update graphics drivers

**"Import error" for PicoGL modules**
   - Install PicoGL: ``pip install picogl``
   - Check Python path and virtual environment

**"File not found" error for data files**
   - Ensure you're running from the examples directory
   - Check that data files exist in the correct location

**Black screen or no rendering**
   - Try legacy examples for better compatibility
   - Check OpenGL support
   - Update graphics drivers

Platform-Specific Issues
~~~~~~~~~~~~~~~~~~~~~~~~

macOS
^^^^^

**Segmentation fault**
   - Run from Terminal.app or iTerm2
   - Check OpenGL drivers
   - Try software rendering

**"No display available" error**
   - Install XQuartz
   - Check DISPLAY environment variable

Windows
^^^^^^^

**"DLL load failed" error**
   - Install Visual C++ Redistributable
   - Check Python architecture (32-bit vs 64-bit)

**"OpenGL not supported" error**
   - Update graphics drivers
   - Check OpenGL support in graphics settings

Linux
^^^^^

**"No display available" error**
   - Ensure X11 or Wayland is running
   - Check DISPLAY environment variable

**"Permission denied" error**
   - Run with appropriate permissions
   - Check file permissions

Example Selection Guide
-----------------------

Choose the right example for your needs:

**Learning OpenGL basics**
   - Start with ``cube.py`` or ``legacy_cube_minimal.py``
   - Try ``teapot.py`` for more complex geometry

**Compatibility issues**
   - Use ``legacy_*_minimal.py`` examples
   - These work on any system with basic OpenGL support

**Advanced features**
   - Try ``molecular_viewer.py`` for complex rendering
   - Explore shader examples in ``glsl/`` directory

**Texture mapping**
   - Use ``texture.py`` or ``tu02/`` shader example
   - Check ``legacy_teapot_fixed.py`` for legacy texture support

**Scientific visualization**
   - Use ``molecular_viewer.py``
   - Check ``examples/README_MOLECULAR.md`` for detailed guide

Customizing Examples
--------------------

You can modify examples to suit your needs:

1. **Change colors**: Modify the color arrays
2. **Add more objects**: Create additional MeshData objects
3. **Change lighting**: Modify shader parameters
4. **Add textures**: Load and apply texture images
5. **Modify controls**: Change keyboard/mouse bindings

For more information, see the :doc:`api/renderer` documentation.

Contributing Examples
---------------------

We welcome contributions of new examples! When contributing:

1. **Follow the existing style** and structure
2. **Include comprehensive comments** explaining the code
3. **Test on multiple platforms** if possible
4. **Provide both modern and legacy versions** when appropriate
5. **Update this documentation** to include your example

For more information, see the :doc:`contributing` guide.
