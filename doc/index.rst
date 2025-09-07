PicoGL Documentation
====================

PicoGL is a lightweight Python OpenGL wrapper designed for educational purposes and simple 3D graphics applications. It provides a clean, easy-to-use interface for OpenGL operations while maintaining compatibility with both modern and legacy OpenGL systems.

.. image:: images/python-badge.png
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: images/opengl-badge.png
   :target: https://www.opengl.org/
   :alt: OpenGL Support

.. image:: images/license-badge.png
   :target: https://opensource.org/licenses/MIT
   :alt: License

Features
--------

* **Cross-platform compatibility**: Works on Windows, macOS, and Linux
* **Legacy OpenGL support**: Compatible with OpenGL 1.x, 2.x, and 3.3+
* **Educational focus**: Clean, well-documented code for learning OpenGL
* **Multiple backends**: Support for both modern and legacy rendering pipelines
* **Comprehensive examples**: From simple cubes to complex molecular visualizations
* **Unit testing**: Full test coverage for all major components

Quick Start
-----------

.. code-block:: python

   from picogl.renderer import MeshData
   from picogl.ui.backend.glut.window.object import RenderWindow
   
   # Create mesh data
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   # Create render window
   window = RenderWindow(width=800, height=600, data=data)
   window.initialize()
   window.run()

Installation
------------

.. code-block:: bash

   # Install from PyPI (when available)
   pip install picogl
   
   # Or install from source
   git clone https://github.com/your-org/picogl.git
   cd picogl
   pip install -e .

Requirements
------------

* Python 3.7+
* PyOpenGL
* NumPy
* PyGLM (for matrix operations)
* Pillow (for texture loading)

Optional Dependencies
---------------------

* PyQt5/PyQt6 (for Qt-based UI backends)
* GLUT (for GLUT-based examples)

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   installation
   quickstart
   examples
   legacy_examples
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/renderer
   api/buffers
   api/shaders
   api/ui
   api/utils

.. toctree::
   :maxdepth: 2
   :caption: Development
   
   development
   testing
   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
