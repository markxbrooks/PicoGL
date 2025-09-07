Legacy Examples
===============

PicoGL includes comprehensive legacy examples designed to work on systems with limited OpenGL support, including older macOS systems and systems without modern shader support.

Overview
--------

The legacy examples provide multiple fallback renderers that work on systems with limited OpenGL support:

* **Minimal versions**: Use only PyOpenGL, maximum compatibility
* **Fixed versions**: Use PicoGL with legacy rendering, medium compatibility
* **Original versions**: Use modern OpenGL 3.3+, low compatibility

Why Legacy Examples?
--------------------

Modern OpenGL (3.3+) requires:
* Shader compilation support
* Vertex Array Objects (VAOs)
* Modern graphics drivers
* Specific OpenGL context requirements

Legacy examples work on:
* Older macOS systems
* Systems without shader support
* Systems with limited OpenGL drivers
* Headless environments (with proper setup)
* Educational environments with restricted OpenGL

Legacy Teapot Examples
----------------------

Legacy Teapot (Minimal)
~~~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_teapot_minimal.py``

The most compatible teapot renderer, using only built-in OpenGL primitives.

**Features**:
* Uses ``glutSolidTeapot()`` built-in primitive
* No external dependencies beyond PyOpenGL
* OpenGL 1.x immediate mode rendering
* Interactive rotation and zoom
* Multiple rendering modes

**Controls**:
* Mouse drag: Rotate view
* Mouse wheel: Zoom in/out
* R: Reset rotation
* W: Toggle wireframe mode
* F: Fill mode
* +/-: Zoom in/out
* Space: Toggle auto-rotation
* ESC: Exit

**Run**:
.. code-block:: bash

   python examples/legacy_teapot_minimal.py

**Compatibility**: Maximum (works on any OpenGL system)

Legacy Teapot (Fixed)
~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_teapot_fixed.py``

PicoGL-integrated legacy teapot with OBJ file support.

**Features**:
* Uses ``LegacyGLMesh`` for OpenGL 1.x/2.x compatibility
* Loads teapot data from OBJ file
* Falls back to wireframe teapot if OBJ loading fails
* Full PicoGL integration
* Interactive controls

**Controls**:
* Mouse drag: Rotate view
* Mouse wheel: Zoom in/out
* R: Reset rotation
* W: Toggle wireframe mode
* F: Fill mode
* +/-: Zoom in/out
* Space: Toggle auto-rotation
* ESC: Exit

**Run**:
.. code-block:: bash

   python examples/legacy_teapot_fixed.py

**Compatibility**: Medium (requires PicoGL library)

Legacy Cube Examples
--------------------

Legacy Cube (Minimal)
~~~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_cube_minimal.py``

The most compatible cube renderer, using immediate mode OpenGL.

**Features**:
* Uses immediate mode OpenGL (``glBegin``/``glEnd``)
* No external dependencies beyond PyOpenGL
* Same vertex and color data as original cube
* Interactive rotation and zoom
* Multiple rendering modes
* Normal vector display

**Controls**:
* Mouse drag: Rotate view
* Mouse wheel: Zoom in/out
* R: Reset rotation
* W: Toggle wireframe mode
* F: Fill mode
* N: Toggle normals display
* +/-: Zoom in/out
* Space: Toggle auto-rotation
* ESC: Exit

**Run**:
.. code-block:: bash

   python examples/legacy_cube_minimal.py

**Compatibility**: Maximum (works on any OpenGL system)

Legacy Cube (Fixed)
~~~~~~~~~~~~~~~~~~~

**File**: ``examples/legacy_cube_fixed.py``

PicoGL-integrated legacy cube using LegacyGLMesh.

**Features**:
* Uses ``LegacyGLMesh`` for OpenGL 1.x/2.x compatibility
* Loads cube data using PicoGL MeshData
* Falls back to wireframe cube if mesh loading fails
* Full PicoGL integration
* Interactive controls

**Controls**:
* Mouse drag: Rotate view
* Mouse wheel: Zoom in/out
* R: Reset rotation
* W: Toggle wireframe mode
* F: Fill mode
* +/-: Zoom in/out
* Space: Toggle auto-rotation
* ESC: Exit

**Run**:
.. code-block:: bash

   python examples/legacy_cube_fixed.py

**Compatibility**: Medium (requires PicoGL library)

Diagnostic Tools
----------------

OpenGL Setup Test
~~~~~~~~~~~~~~~~~

**File**: ``examples/test_opengl_setup.py``

Comprehensive diagnostic tool for OpenGL setup issues.

**Features**:
* Tests OpenGL imports
* Tests display environment
* Tests OpenGL context creation
* Tests PicoGL imports
* Provides troubleshooting guidance

**Run**:
.. code-block:: bash

   python examples/test_opengl_setup.py

**Output**: Detailed report of OpenGL capabilities and issues

Cube Data Test
~~~~~~~~~~~~~~

**File**: ``examples/test_cube_data.py``

Tests cube data structure and PicoGL imports without requiring a display.

**Features**:
* Validates cube vertex and color data
* Tests triangle structure
* Tests PicoGL imports
* Tests mesh creation
* Provides troubleshooting guidance

**Run**:

.. code-block:: bash

   python examples/test_cube_data.py

**Output**: Validation report of cube data and imports

Installation and Setup
----------------------

Prerequisites
~~~~~~~~~~~~~

**Minimal Examples**:
* Python 3.7+
* PyOpenGL
* GLUT (usually included with PyOpenGL)

**Fixed Examples**:
* Python 3.7+
* PyOpenGL
* GLUT
* NumPy
* PicoGL library

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install minimal requirements
   pip install PyOpenGL PyOpenGL_accelerate numpy
   
   # For fixed examples (PicoGL integration)
   pip install picogl

Platform-Specific Setup
~~~~~~~~~~~~~~~~~~~~~~~~

macOS
^^^^^

1. **Install XQuartz** (for X11 support):
   .. code-block:: bash

      brew install --cask xquartz

2. **Run from Terminal.app or iTerm2** (not from IDE)

3. **Check OpenGL support**:
   .. code-block:: python

      import OpenGL.GL as GL
      print(GL.glGetString(GL.GL_VERSION))

Windows
^^^^^^^

1. **Update graphics drivers** to latest version

2. **Install Visual C++ Redistributable** if needed

3. **Run from command prompt** (not from IDE)

Linux
^^^^^

1. **Install OpenGL libraries**:
   .. code-block:: bash

      # Ubuntu/Debian
      sudo apt install libgl1-mesa-dev libglu1-mesa
      
      # CentOS/RHEL
      sudo yum install mesa-libGL mesa-libGLU

2. **Ensure X11 or Wayland is running**

3. **Check display environment**:
   .. code-block:: bash

      echo $DISPLAY

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**"No OpenGL context" error**
   - Use minimal versions instead
   - Run from Terminal.app (macOS) or command prompt (Windows)
   - Check display environment

**"Shader compilation failed" error**
   - Use minimal versions (no shaders required)
   - Check OpenGL version support
   - Update graphics drivers

**"PicoGL import failed" error**
   - Use minimal versions (no PicoGL required)
   - Or install PicoGL: ``pip install picogl``

**"Segmentation fault" error**
   - Use minimal versions
   - Check OpenGL drivers
   - Try software rendering

**"Black screen" error**
   - Check OpenGL support
   - Use minimal versions
   - Try different OpenGL settings

**"No display available" error**
   - Check display environment
   - Install XQuartz (macOS)
   - Ensure X11/Wayland is running (Linux)

macOS Specific Issues
~~~~~~~~~~~~~~~~~~~~~

**OpenGL context creation fails**
   - Run from Terminal.app or iTerm2
   - Check if XQuartz is installed and running
   - Try software rendering: ``export MESA_GL_VERSION_OVERRIDE=3.3``

**Segmentation fault**
   - Run from Terminal.app
   - Check OpenGL drivers
   - Try different OpenGL settings

**"No display available" error**
   - Install XQuartz: ``brew install --cask xquartz``
   - Check DISPLAY environment variable
   - Restart XQuartz

Windows Specific Issues
~~~~~~~~~~~~~~~~~~~~~~~

**"DLL load failed" error**
   - Install Visual C++ Redistributable
   - Check Python architecture (32-bit vs 64-bit)

**"OpenGL not supported" error**
   - Update graphics drivers
   - Check OpenGL support in graphics settings

**"Microsoft Visual C++ 14.0 is required"**
   - Install Visual Studio Build Tools
   - Or install pre-compiled wheels

Linux Specific Issues
~~~~~~~~~~~~~~~~~~~~~

**"No display available" error**
   - Ensure X11 or Wayland is running
   - Check DISPLAY environment variable

**"OpenGL not supported" error**
   - Install mesa libraries
   - Check graphics drivers

**"Permission denied" error**
   - Run with appropriate permissions
   - Check file permissions

Performance Notes
-----------------

**Minimal Versions**:
* Fastest performance
* Uses hardware-optimized primitives
* Immediate mode rendering
* No shader compilation overhead

**Fixed Versions**:
* Medium performance
* Uses legacy VBOs
* Some shader compilation
* Better integration with PicoGL

**Original Versions**:
* Slowest performance
* Full shader pipeline
* Modern VAO/VBO usage
* Maximum feature set

Choosing the Right Version
--------------------------

**Use Minimal Versions When**:
* Maximum compatibility is required
* OpenGL support is limited
* Performance is critical
* No PicoGL integration needed

**Use Fixed Versions When**:
* PicoGL integration is desired
* Some OpenGL support is available
* Balance between compatibility and features
* OBJ file loading is needed

**Use Original Versions When**:
* Full OpenGL 3.3+ support is available
* Maximum features are needed
* Modern shader pipeline is required
* Best visual quality is desired

Development Notes
-----------------

**Adding New Legacy Examples**:

1. **Follow the naming convention**: ``legacy_<name>_<type>.py``
2. **Provide both minimal and fixed versions** when possible
3. **Include comprehensive error handling**
4. **Test on multiple platforms**
5. **Document compatibility requirements**

**Example Structure**:
.. code-block:: python

   class LegacyExampleRenderer:
       def __init__(self, width=800, height=600, title="Example"):
           # Initialize renderer
           
       def init_glut(self):
           # Initialize GLUT window
           
       def init_gl(self):
           # Initialize OpenGL state
           
       def display(self):
           # Render the scene
           
       def run(self):
           # Main loop

**Error Handling**:
.. code-block:: python

   try:
       # OpenGL operations
   except Exception as e:
       print(f"Warning: OpenGL issue: {e}")
       # Fallback behavior

For more information, see the :doc:`contributing` guide.

License
-------

The legacy examples are part of the PicoGL project and follow the same license terms.
