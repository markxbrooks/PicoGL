Installation
============

PicoGL can be installed from source or from PyPI (when available). This guide covers installation on different platforms and troubleshooting common issues.

Prerequisites
-------------

Before installing PicoGL, ensure you have the following:

* **Python 3.7 or higher**
* **OpenGL drivers** for your graphics card
* **Development tools** (for building from source)

Platform-Specific Requirements
-------------------------------

Windows
~~~~~~~

1. **Install Python 3.7+** from `python.org <https://www.python.org/downloads/>`_
2. **Install Visual Studio Build Tools** (for compiling extensions)
3. **Update graphics drivers** to the latest version

.. code-block:: bash

   # Install PicoGL
   pip install picogl
   
   # Or install with all dependencies
   pip install picogl[all]

macOS
~~~~~

1. **Install Python 3.7+** using Homebrew or from python.org
2. **Install Xcode Command Line Tools**:

   .. code-block:: bash

      xcode-select --install

3. **Install XQuartz** (for X11 support):

   .. code-block:: bash

      brew install --cask xquartz

.. code-block:: bash

   # Install PicoGL
   pip install picogl
   
   # Or install with all dependencies
   pip install picogl[all]

Linux (Ubuntu/Debian)
~~~~~~~~~~~~~~~~~~~~~

1. **Install Python 3.7+** and development tools:

   .. code-block:: bash

      sudo apt update
      sudo apt install python3 python3-pip python3-dev
      sudo apt install build-essential libgl1-mesa-dev

2. **Install OpenGL libraries**:

   .. code-block:: bash

      sudo apt install libgl1-mesa-glx libglu1-mesa

.. code-block:: bash

   # Install PicoGL
   pip install picogl
   
   # Or install with all dependencies
   pip install picogl[all]

Linux (CentOS/RHEL/Fedora)
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Install Python 3.7+** and development tools:

   .. code-block:: bash

      # CentOS/RHEL
      sudo yum install python3 python3-pip python3-devel
      sudo yum groupinstall "Development Tools"
      
      # Fedora
      sudo dnf install python3 python3-pip python3-devel
      sudo dnf groupinstall "Development Tools"

2. **Install OpenGL libraries**:

   .. code-block:: bash

      # CentOS/RHEL
      sudo yum install mesa-libGL mesa-libGLU
      
      # Fedora
      sudo dnf install mesa-libGL mesa-libGLU

.. code-block:: bash

   # Install PicoGL
   pip install picogl
   
   # Or install with all dependencies
   pip install picogl[all]

Installation Methods
--------------------

From PyPI (Recommended) *Coming Soon!
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install picogl

From Source
~~~~~~~~~~~

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/your-org/picogl.git
      cd picogl

2. **Install in development mode**:

   .. code-block:: bash

      pip install -e .

3. **Install with all dependencies**:

   .. code-block:: bash

      pip install -e .[all]

From Conda *Coming Soon!
~~~~~~~~~~

.. code-block:: bash

   conda install -c conda-forge picogl

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

* **PyOpenGL**: Python bindings for OpenGL
* **PyOpenGL-accelerate**: Accelerated OpenGL operations
* **NumPy**: Numerical computing library
* **PyGLM**: OpenGL Mathematics library

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

* **Pillow**: Image processing for texture loading
* **PyQt5/PyQt6**: Qt-based UI backends
* **GLUT**: GLUT-based examples

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

* **pytest**: Testing framework
* **pytest-cov**: Coverage testing
* **black**: Code formatting
* **flake8**: Linting
* **mypy**: Type checking

Installation Verification
-------------------------

After installation, verify that PicoGL is working correctly:

.. code-block:: python

   import picogl
   print(f"PicoGL version: {picogl.__version__}")
   
   # Test basic functionality
   from picogl.renderer import MeshData
   import numpy as np
   
   # Create simple mesh data
   vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
   colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
   
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   print("✅ PicoGL installation successful!")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'OpenGL'**
   Install PyOpenGL: ``pip install PyOpenGL PyOpenGL-accelerate``

**ImportError: No module named 'numpy'**
   Install NumPy: ``pip install numpy``

**ImportError: No module named 'pyglm'**
   Install PyGLM: ``pip install pyglm``

**OpenGL context creation failed**
   Update graphics drivers and ensure OpenGL is supported

**Segmentation fault on macOS**
   Run from Terminal.app or iTerm2, not from IDE

**Black screen or no rendering**
   Check OpenGL support and try software rendering

macOS Specific Issues
~~~~~~~~~~~~~~~~~~~~~

**"No OpenGL context" error**
   - Run from Terminal.app or iTerm2
   - Check if XQuartz is installed and running
   - Try software rendering: ``export MESA_GL_VERSION_OVERRIDE=3.3``

**"Shader compilation failed" error**
   - Use legacy examples instead
   - Check OpenGL version support

**"Segmentation fault" error**
   - Run from Terminal.app
   - Check OpenGL drivers
   - Try different OpenGL settings

Windows Specific Issues
~~~~~~~~~~~~~~~~~~~~~~~

**"Microsoft Visual C++ 14.0 is required"**
   - Install Visual Studio Build Tools
   - Or install pre-compiled wheels

**"OpenGL not supported" error**
   - Update graphics drivers
   - Check if OpenGL is enabled in graphics settings

**"DLL load failed" error**
   - Install Visual C++ Redistributable
   - Check Python architecture (32-bit vs 64-bit)

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

Getting Help
------------

If you encounter issues not covered here:

1. **Check the troubleshooting guide** in the documentation
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information about your system
4. **Join the community** discussions

System Information
------------------

When reporting issues, please include:

* Operating system and version
* Python version
* Graphics card and drivers
* OpenGL version
* Complete error message
* Steps to reproduce the issue

.. code-block:: python

   import sys
   import platform
   import OpenGL.GL as GL
   
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   print(f"OpenGL: {GL.glGetString(GL.GL_VERSION)}")
   print(f"Vendor: {GL.glGetString(GL.GL_VENDOR)}")
   print(f"Renderer: {GL.glGetString(GL.GL_RENDERER)}")
