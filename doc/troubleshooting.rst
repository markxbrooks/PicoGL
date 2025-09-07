Troubleshooting
===============

This guide helps you diagnose and fix common issues with PicoGL.

Common Issues
-------------

Installation Problems
~~~~~~~~~~~~~~~~~~~~~

**"No module named 'picogl'" error**
   - Ensure PicoGL is installed: ``pip install picogl``
   - Check Python path and virtual environment
   - Verify installation: ``python -c "import picogl"``

**"No module named 'OpenGL'" error**
   - Install PyOpenGL: ``pip install PyOpenGL PyOpenGL-accelerate``
   - Check OpenGL installation on your system

**"No module named 'numpy'" error**
   - Install NumPy: ``pip install numpy``
   - Check NumPy version compatibility

**"No module named 'pyglm'" error**
   - Install PyGLM: ``pip install pyglm``
   - Check PyGLM version compatibility

**"No module named 'PIL'" error**
   - Install Pillow: ``pip install Pillow``
   - Check Pillow version compatibility

OpenGL Context Issues
~~~~~~~~~~~~~~~~~~~~~

**"No OpenGL context" error**
   - Run from Terminal.app (macOS) or command prompt (Windows)
   - Check display environment variables
   - Verify OpenGL drivers are installed

**"OpenGL context creation failed" error**
   - Update graphics drivers
   - Check OpenGL support on your system
   - Try software rendering

**"Segmentation fault" error**
   - Run from Terminal.app (macOS)
   - Check OpenGL drivers
   - Try different OpenGL settings

**"Black screen" or no rendering**
   - Check OpenGL support
   - Try legacy examples for better compatibility
   - Update graphics drivers

Shader Compilation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**"Shader compilation failed" error**
   - Use legacy examples (no shaders required)
   - Check OpenGL version support
   - Update graphics drivers

**"Shader link failed" error**
   - Check shader compatibility
   - Verify shader source code
   - Check OpenGL version

**"Uniform not found" error**
   - Check uniform names in shaders
   - Verify uniform types
   - Check shader program binding

**"Texture loading failed" error**
   - Check texture file format
   - Verify texture file path
   - Check OpenGL texture support

Platform-Specific Issues
------------------------

macOS Issues
~~~~~~~~~~~~

**"No display available" error**
   - Install XQuartz: ``brew install --cask xquartz``
   - Check DISPLAY environment variable
   - Restart XQuartz

**"OpenGL not supported" error**
   - Check OpenGL version: ``python -c "import OpenGL.GL as GL; print(GL.glGetString(GL.GL_VERSION))"``
   - Update graphics drivers
   - Try software rendering

**"Segmentation fault" error**
   - Run from Terminal.app or iTerm2
   - Check OpenGL drivers
   - Try different OpenGL settings

**"Shader compilation failed" error**
   - Use legacy examples instead
   - Check OpenGL version support
   - Try software rendering

**Troubleshooting Steps**:
1. Run from Terminal.app or iTerm2
2. Check OpenGL version and support
3. Install XQuartz if needed
4. Try legacy examples for compatibility
5. Update graphics drivers

Windows Issues
~~~~~~~~~~~~~~

**"DLL load failed" error**
   - Install Visual C++ Redistributable
   - Check Python architecture (32-bit vs 64-bit)
   - Reinstall PyOpenGL

**"OpenGL not supported" error**
   - Update graphics drivers
   - Check OpenGL support in graphics settings
   - Try software rendering

**"Microsoft Visual C++ 14.0 is required" error**
   - Install Visual Studio Build Tools
   - Or install pre-compiled wheels

**"Permission denied" error**
   - Run as administrator
   - Check file permissions
   - Check antivirus software

**Troubleshooting Steps**:
1. Update graphics drivers
2. Install Visual C++ Redistributable
3. Check Python architecture
4. Try running as administrator
5. Check antivirus software

Linux Issues
~~~~~~~~~~~~

**"No display available" error**
   - Ensure X11 or Wayland is running
   - Check DISPLAY environment variable
   - Install display server

**"OpenGL not supported" error**
   - Install mesa libraries: ``sudo apt install libgl1-mesa-dev libglu1-mesa``
   - Check graphics drivers
   - Try software rendering

**"Permission denied" error**
   - Run with appropriate permissions
   - Check file permissions
   - Check SELinux/AppArmor

**"Library not found" error**
   - Install required libraries
   - Check library paths
   - Update package manager

**Troubleshooting Steps**:
1. Install mesa libraries
2. Check display server
3. Update graphics drivers
4. Check library paths
5. Try software rendering

Performance Issues
------------------

Slow Rendering
~~~~~~~~~~~~~~

**Causes**:
* Too many draw calls
* Inefficient shaders
* Large textures
* Poor buffer management

**Solutions**:
* Use instanced rendering
* Optimize shaders
* Use appropriate texture sizes
* Batch similar operations

**Example**:

.. code-block:: python

   # Inefficient rendering
   for obj in objects:
       obj.render()  # Many draw calls
   
   # Efficient rendering
   batch_objects(objects)
   render_batch()  # Single draw call

Memory Issues
~~~~~~~~~~~~~

**Causes**:
* Large textures
* Too many buffers
* Memory leaks
* Inefficient data structures

**Solutions**:
* Use appropriate texture sizes
* Clean up unused buffers
* Monitor memory usage
* Use efficient data types

**Example**:

.. code-block:: python

   # Memory leak
   def create_mesh():
       vao = VertexArrayObject()
       # ... use vao ...
       # Forgot to delete vao
   
   # Fixed
   def create_mesh():
       vao = VertexArrayObject()
       try:
           # ... use vao ...
       finally:
           vao.delete()

Frame Rate Issues
~~~~~~~~~~~~~~~~~

**Causes**:
* VSync enabled
* Too many operations per frame
* Inefficient rendering
* Poor OpenGL state management

**Solutions**:
* Disable VSync if needed
* Optimize rendering loop
* Use efficient rendering techniques
* Minimize state changes

**Example**:

.. code-block:: python

   # Inefficient rendering
   def render():
       glEnable(GL_DEPTH_TEST)
       draw_object1()
       glDisable(GL_DEPTH_TEST)
       glEnable(GL_DEPTH_TEST)
       draw_object2()
   
   # Efficient rendering
   def render():
       glEnable(GL_DEPTH_TEST)
       draw_object1()
       draw_object2()
       glDisable(GL_DEPTH_TEST)

Debugging Techniques
--------------------

Enable Debug Output
~~~~~~~~~~~~~~~~~~~

**OpenGL Error Checking**:

.. code-block:: python

   def check_gl_error():
       error = glGetError()
       if error != GL_NO_ERROR:
           print(f"OpenGL error: {error}")
           return False
       return True
   
   # Use after OpenGL calls
   glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_INT, None)
   check_gl_error()

**Debug Information**:

.. code-block:: python

   def print_gl_info():
       print(f"OpenGL version: {glGetString(GL_VERSION)}")
       print(f"Vendor: {glGetString(GL_VENDOR)}")
       print(f"Renderer: {glGetString(GL_RENDERER)}")
       print(f"Extensions: {glGetString(GL_EXTENSIONS)}")

**Performance Profiling**:

.. code-block:: python

   import time
   
   def profile_render():
       start_time = time.time()
       self.render_scene()
       end_time = time.time()
       frame_time = end_time - start_time
       fps = 1.0 / frame_time
       print(f"Frame time: {frame_time:.3f}s, FPS: {fps:.1f}")

Use Diagnostic Tools
~~~~~~~~~~~~~~~~~~~~

**OpenGL Setup Test**:

.. code-block:: bash

   python examples/test_opengl_setup.py

**Cube Data Test**:

.. code-block:: bash

   python examples/test_cube_data.py

**Legacy Examples**:

.. code-block:: bash

   # Try minimal examples for compatibility
   python examples/legacy_cube_minimal.py
   python examples/legacy_teapot_minimal.py

Check System Information
~~~~~~~~~~~~~~~~~~~~~~~~

**Python Information**:

.. code-block:: python

   import sys
   import platform
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   print(f"Architecture: {platform.architecture()}")

**OpenGL Information**:

.. code-block:: python

   import OpenGL.GL as GL
   print(f"OpenGL version: {GL.glGetString(GL.GL_VERSION)}")
   print(f"Vendor: {GL.glGetString(GL.GL_VENDOR)}")
   print(f"Renderer: {GL.glGetString(GL.GL_RENDERER)}")

**Package Information**:

.. code-block:: python

   import pkg_resources
   packages = ['picogl', 'numpy', 'PyOpenGL', 'pyglm', 'Pillow']
   for package in packages:
       try:
           version = pkg_resources.get_distribution(package).version
           print(f"{package}: {version}")
       except pkg_resources.DistributionNotFound:
           print(f"{package}: Not installed")

Common Solutions
----------------

Try Legacy Examples
~~~~~~~~~~~~~~~~~~~

If modern examples don't work, try legacy examples:

.. code-block:: bash

   # Minimal examples (maximum compatibility)
   python examples/legacy_cube_minimal.py
   python examples/legacy_teapot_minimal.py
   
   # Fixed examples (PicoGL integration)
   python examples/legacy_cube_fixed.py
   python examples/legacy_teapot_fixed.py

Update Dependencies
~~~~~~~~~~~~~~~~~~~

Update all dependencies to latest versions:

.. code-block:: bash

   pip install --upgrade picogl numpy PyOpenGL PyOpenGL-accelerate pyglm Pillow

Check OpenGL Support
~~~~~~~~~~~~~~~~~~~~

Verify OpenGL support on your system:

.. code-block:: python

   import OpenGL.GL as GL
   
   # Check OpenGL version
   version = GL.glGetString(GL.GL_VERSION)
   print(f"OpenGL version: {version}")
   
   # Check extensions
   extensions = GL.glGetString(GL.GL_EXTENSIONS)
   print(f"Extensions: {extensions}")

Use Software Rendering
~~~~~~~~~~~~~~~~~~~~~~

If hardware rendering fails, try software rendering:

.. code-block:: bash

   # Set environment variable
   export MESA_GL_VERSION_OVERRIDE=3.3
   python examples/cube.py

Check Display Environment
~~~~~~~~~~~~~~~~~~~~~~~~~

Verify display environment:

.. code-block:: bash

   # Check display
   echo $DISPLAY
   
   # Check X11
   xdpyinfo
   
   # Check Wayland
   echo $WAYLAND_DISPLAY

Report Issues
-------------

When reporting issues, include:

1. **System Information**:
   - Operating system and version
   - Python version
   - Graphics card and drivers
   - OpenGL version

2. **Error Information**:
   - Complete error message
   - Steps to reproduce
   - Expected vs actual behavior

3. **Environment Information**:
   - Virtual environment details
   - Package versions
   - Display environment

4. **Code Information**:
   - Minimal code to reproduce
   - Full traceback
   - Relevant configuration

**Example Issue Report**:

.. code-block:: text

   **System**: macOS 12.0, Python 3.9, Intel HD Graphics 6000
   **Error**: "No OpenGL context" when running cube.py
   **Steps**: 
   1. Install PicoGL: pip install picogl
   2. Run: python examples/cube.py
   3. Get error: "No OpenGL context"
   **Expected**: Cube window should appear
   **Actual**: Error message and no window
   **Code**: Standard cube.py example
   **Environment**: Terminal.app, XQuartz installed

Getting Help
------------

**Documentation**:
* Check this troubleshooting guide
* Read the API documentation
* Look at example code

**Community**:
* Search existing issues on GitHub
* Create a new issue with detailed information
* Join community discussions

**Professional Support**:
* Contact maintainers directly
* Consider commercial support options
* Hire OpenGL experts for complex issues

**Resources**:
* OpenGL documentation
* PyOpenGL documentation
* Platform-specific OpenGL guides
* Graphics driver documentation

Remember: Most issues can be resolved by using the appropriate legacy examples for your system's OpenGL capabilities.
