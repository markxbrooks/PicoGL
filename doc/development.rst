Development
===========

This section provides information for developers who want to contribute to PicoGL or understand its internal architecture.

Project Structure
-----------------

PicoGL follows a modular architecture with clear separation of concerns:

.. code-block:: text

   picogl/
   ├── backend/           # OpenGL backend implementations
   │   ├── modern/        # Modern OpenGL 3.3+ backend
   │   └── legacy/        # Legacy OpenGL 1.x/2.x backend
   ├── buffers/           # Buffer management
   │   ├── vertex/        # Vertex buffer implementations
   │   └── attributes/    # Attribute specifications
   ├── renderer/          # Core rendering classes
   │   ├── meshdata.py    # Mesh data management
   │   ├── object.py      # Object renderer
   │   └── texture.py     # Texture renderer
   ├── shaders/           # Shader management
   │   ├── compile.py     # Shader compilation
   │   ├── load.py        # Shader loading
   │   └── manager.py     # Shader manager
   ├── ui/                # User interface
   │   └── backend/       # UI backends (GLUT, Qt)
   ├── utils/             # Utility functions
   │   ├── loader/        # Data loaders
   │   └── texture.py     # Texture utilities
   └── tests/             # Unit tests

Architecture Overview
---------------------

PicoGL uses a layered architecture:

**Application Layer**
   - User applications and examples
   - High-level API usage

**Renderer Layer**
   - ObjectRenderer, TextureRenderer
   - MeshData, GLContext
   - High-level rendering abstractions

**Backend Layer**
   - Modern OpenGL 3.3+ implementation
   - Legacy OpenGL 1.x/2.x implementation
   - Platform-specific optimizations

**OpenGL Layer**
   - Direct OpenGL calls
   - Buffer management
   - Shader compilation

**Platform Layer**
   - GLUT, Qt backends
   - Input handling
   - Window management

Design Principles
-----------------

**Compatibility First**
   - Support for both modern and legacy OpenGL
   - Graceful degradation when features unavailable
   - Cross-platform compatibility

**Educational Focus**
   - Clean, well-documented code
   - Clear separation of concerns
   - Easy to understand and modify

**Performance Aware**
   - Efficient rendering pipelines
   - Minimal overhead
   - Platform-specific optimizations

**Extensible Design**
   - Modular architecture
   - Plugin system for backends
   - Easy to add new features

Backend System
--------------

Modern Backend
~~~~~~~~~~~~~~

The modern backend provides OpenGL 3.3+ functionality:

**Features**:
* Vertex Array Objects (VAOs)
* Modern shader pipeline
* Advanced uniform types
* Efficient buffer management

**Key Classes**:
* ``VertexArrayObject``: VAO management
* ``ModernVBO``: Modern vertex buffers
* ``ModernEBO``: Modern element buffers
* ``ShaderProgram``: Shader management

**Example**:

.. code-block:: python

   from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
   
   # Create VAO
   vao = VertexArrayObject()
   vao.add_vbo(index=0, data=vertices, size=3)
   vao.add_vbo(index=1, data=colors, size=3)
   vao.add_ebo(data=indices)
   
   # Draw
   with vao:
       vao.draw(mode=GL_TRIANGLES, index_count=len(indices))

Legacy Backend
~~~~~~~~~~~~~~

The legacy backend provides OpenGL 1.x/2.x compatibility:

**Features**:
* Immediate mode rendering
* Legacy VBOs
* Fixed function pipeline
* Client state management

**Key Classes**:
* ``VertexBufferGroup``: Legacy buffer management
* ``LegacyVBO``: Legacy vertex buffers
* ``LegacyEBO``: Legacy element buffers
* ``LegacyGLMesh``: Legacy mesh rendering

**Example**:

.. code-block:: python

   from picogl.buffers.vertex.legacy import VertexBufferGroup
   
   # Create vertex buffer group
   vbg = VertexBufferGroup()
   vbg.add_vbo(name="position", data=vertices, size=3)
   vbg.add_vbo(name="color", data=colors, size=3)
   vbg.add_ebo(data=indices)
   
   # Draw
   vbg.bind()
   vbg.draw(mode=GL_TRIANGLES)
   vbg.unbind()

Backend Selection
~~~~~~~~~~~~~~~~~

PicoGL automatically selects the appropriate backend:

.. code-block:: python

   def select_backend():
       if has_modern_opengl():
           return ModernBackend()
       elif has_legacy_opengl():
           return LegacyBackend()
       else:
           return ImmediateModeBackend()

Testing Framework
-----------------

Unit Tests
~~~~~~~~~~

PicoGL includes comprehensive unit tests:

**Test Structure**

.. code-block:: text

   tests/
   ├── test_vertex_array_object.py
   ├── test_vertex_buffer_group.py
   ├── test_meshdata.py
   ├── test_glmesh.py
   ├── test_legacy_glmesh.py
   ├── test_object_renderer.py
   └── test_texture_renderer.py

**Running Tests**:

.. code-block:: bash

   # Run all tests
   python -m unittest discover tests
   
   # Run specific test
   python -m unittest tests.test_vertex_array_object
   
   # Run with coverage
   python -m pytest tests/ --cov=picogl

**Test Features**:
* Mock OpenGL functions to avoid context requirements
* Comprehensive error handling tests
* Edge case testing
* Performance benchmarks

**Example Test**:

.. code-block:: python

   import unittest
   from unittest.mock import MagicMock, patch
   from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
   
   class TestVertexArrayObject(unittest.TestCase):
       def setUp(self):
           # Mock OpenGL functions
           self.gl_patches = [
               patch('picogl.backend.modern.core.vertex.array.object.glGenVertexArrays'),
               patch('picogl.backend.modern.core.vertex.array.object.glBindVertexArray'),
               # ... more patches
           ]
           for patch_obj in self.gl_patches:
               patch_obj.start()
       
       def tearDown(self):
           for patch_obj in self.gl_patches:
               patch_obj.stop()
       
       def test_initialization(self):
           vao = VertexArrayObject()
           self.assertIsNotNone(vao)

Integration Tests
~~~~~~~~~~~~~~~~~

Integration tests verify end-to-end functionality:

**Test Categories**:
* Rendering pipeline tests
* Cross-platform compatibility tests
* Performance regression tests
* Memory leak tests

**Example**:

.. code-block:: python

   def test_rendering_pipeline():
       # Create mesh data
       data = MeshData.from_raw(vertices=vertices, colors=colors)
       
       # Create renderer
       renderer = ObjectRenderer(context=context, data=data)
       
       # Test initialization
       renderer.initialize_shaders()
       renderer.initialize()
       
       # Test rendering
       renderer.render()
       
       # Verify no errors
       self.assertFalse(has_gl_errors())

Build System
------------

Setup Configuration
~~~~~~~~~~~~~~~~~~~

PicoGL uses setuptools for packaging:

**pyproject.toml**:

.. code-block:: toml

   [build-system]
   requires = ["setuptools>=45", "wheel"]
   build-backend = "setuptools.build_meta"
   
   [project]
   name = "picogl"
   version = "1.0.0"
   description = "Lightweight Python OpenGL wrapper"
   requires-python = ">=3.7"
   dependencies = [
       "numpy>=1.19.0",
       "PyOpenGL>=3.1.0",
       "PyOpenGL-accelerate>=3.1.0",
       "pyglm>=2.0.0",
       "Pillow>=8.0.0"
   ]
   
   [project.optional-dependencies]
   dev = [
       "pytest>=6.0.0",
       "pytest-cov>=2.0.0",
       "black>=21.0.0",
       "flake8>=3.8.0",
       "mypy>=0.800"
   ]
   qt = [
       "PyQt5>=5.15.0",
       "PyQt6>=6.0.0"
   ]

**setup.py**:

.. code-block:: python

   from setuptools import setup, find_packages
   
   setup(
       name="picogl",
       version="1.0.0",
       packages=find_packages(),
       python_requires=">=3.7",
       install_requires=[
           "numpy>=1.19.0",
           "PyOpenGL>=3.1.0",
           "PyOpenGL-accelerate>=3.1.0",
           "pyglm>=2.0.0",
           "Pillow>=8.0.0"
       ],
       extras_require={
           "dev": [
               "pytest>=6.0.0",
               "pytest-cov>=2.0.0",
               "black>=21.0.0",
               "flake8>=3.8.0",
               "mypy>=0.800"
           ],
           "qt": [
               "PyQt5>=5.15.0",
               "PyQt6>=6.0.0"
           ]
       }
   )

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

**Core Dependencies**:
* Python 3.7+
* NumPy
* PyOpenGL
* PyGLM
* Pillow

**Development Dependencies**:
* pytest: Testing framework
* pytest-cov: Coverage testing
* black: Code formatting
* flake8: Linting
* mypy: Type checking

**Installation**:

.. code-block:: bash

   # Install in development mode
   pip install -e .
   
   # Install with development dependencies
   pip install -e .[dev]
   
   # Install with all optional dependencies
   pip install -e .[dev,qt]

Code Style
----------

Formatting
~~~~~~~~~~

PicoGL uses Black for code formatting:

**Configuration**:

.. code-block:: toml

   [tool.black]
   line-length = 88
   target-version = ['py37']
   include = '\.pyi?$'
   extend-exclude = '''
   /(
       \.git
     | \.mypy_cache
     | \.tox
     | \.venv
     | _build
     | buck-out
     | build
     | dist
   )/
   '''

**Usage**:

.. code-block:: bash

   # Format all Python files
   black picogl/
   
   # Check formatting
   black --check picogl/

Linting
~~~~~~~

PicoGL uses flake8 for linting:

**Configuration**:

.. code-block:: ini

   [flake8]
   max-line-length = 88
   extend-ignore = E203, W503
   exclude = 
       .git,
       __pycache__,
       .venv,
       _build,
       dist

**Usage**:

.. code-block:: bash

   # Lint all Python files
   flake8 picogl/
   
   # Lint specific file
   flake8 picogl/renderer/meshdata.py

Type Checking
~~~~~~~~~~~~~

PicoGL uses mypy for type checking:

**Configuration**:

.. code-block:: ini

   [mypy]
   python_version = 3.7
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = True
   disallow_incomplete_defs = True
   check_untyped_defs = True
   disallow_untyped_decorators = True
   no_implicit_optional = True
   warn_redundant_casts = True
   warn_unused_ignores = True
   warn_no_return = True
   warn_unreachable = True
   strict_equality = True

**Usage**:

.. code-block:: bash

   # Type check all Python files
   mypy picogl/
   
   # Type check specific file
   mypy picogl/renderer/meshdata.py

Documentation
-------------

Sphinx Configuration
~~~~~~~~~~~~~~~~~~~~

PicoGL uses Sphinx for documentation:

**conf.py**:

.. code-block:: python

   import os
   import sys
   
   sys.path.insert(0, os.path.abspath('..'))
   
   project = 'PicoGL'
   copyright = '2025, PicoGL Contributors'
   author = 'PicoGL Contributors'
   release = '1.0.0'
   
   extensions = [
       'sphinx.ext.autodoc',
       'sphinx.ext.viewcode',
       'sphinx.ext.napoleon',
       'sphinx.ext.intersphinx',
       'sphinx.ext.todo',
       'sphinx.ext.coverage',
       'sphinx.ext.mathjax',
       'sphinx.ext.ifconfig',
       'sphinx.ext.githubpages',
   ]
   
   html_theme = 'sphinx_rtd_theme'
   latex_engine = 'xelatex'

**Building Documentation**:

.. code-block:: bash

   # Build HTML documentation
   sphinx-build -b html doc/ doc/_build/html
   
   # Build PDF documentation
   sphinx-build -b latex doc/ doc/_build/latex
   cd doc/_build/latex && make

Docstring Style
~~~~~~~~~~~~~~~

PicoGL uses Sphinx/RST-style docstrings:

**Example**:

.. code-block:: python

   def create_mesh_data(vertices, colors, normals=None):
       """Create mesh data from vertex information.
       
       :param vertices: Array of vertex positions (N, 3)
       :param colors: Array of vertex colors (N, 3)
       :param normals: Optional array of vertex normals (N, 3)
       :returns: MeshData: Mesh data object
       :raises: ValueError: If vertices or colors are invalid
               TypeError: If input types are incorrect
       """
       pass

Contributing
------------

Getting Started
~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**
4. **Make your changes**
5. **Add tests** for new functionality
6. **Run the test suite**
7. **Submit a pull request**

**Example**:

.. code-block:: bash

   # Fork and clone
   git clone https://github.com/your-username/picogl.git
   cd picogl
   
   # Create feature branch
   git checkout -b feature/new-feature
   
   # Make changes
   # ... edit files ...
   
   # Run tests
   python -m unittest discover tests
   
   # Commit changes
   git add .
   git commit -m "Add new feature"
   
   # Push to fork
   git push origin feature/new-feature
   
   # Create pull request on GitHub

Code Review Process
~~~~~~~~~~~~~~~~~~~

**Pull Request Requirements**:
* All tests must pass
* Code must be formatted with Black
* Code must pass flake8 linting
* Code must pass mypy type checking
* New functionality must have tests
* Documentation must be updated

**Review Checklist**:
* [ ] Code follows project style guidelines
* [ ] Tests cover new functionality
* [ ] Documentation is updated
* [ ] No breaking changes without discussion
* [ ] Performance impact is considered
* [ ] Cross-platform compatibility is maintained

Release Process
---------------

Version Numbering
~~~~~~~~~~~~~~~~~

PicoGL uses semantic versioning (MAJOR.MINOR.PATCH):

* **MAJOR**: Breaking changes
* **MINOR**: New features (backward compatible)
* **PATCH**: Bug fixes (backward compatible)

**Examples**:
* 1.0.0: Initial release
* 1.1.0: New features added
* 1.1.1: Bug fixes
* 2.0.0: Breaking changes

Release Steps
~~~~~~~~~~~~~

1. **Update version numbers** in all relevant files
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** to ensure everything works
4. **Build documentation** and verify it's correct
5. **Create release tag** on GitHub
6. **Build and upload** to PyPI
7. **Announce release** to community

**Example**:

.. code-block:: bash

   # Update version
   sed -i 's/version = "1.0.0"/version = "1.1.0"/' pyproject.toml
   
   # Update changelog
   # ... edit CHANGELOG.md ...
   
   # Run tests
   python -m unittest discover tests
   
   # Build documentation
   sphinx-build -b html doc/ doc/_build/html
   
   # Create tag
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   
   # Build and upload
   python -m build
   python -m twine upload dist/*

Performance Considerations
-------------------------

Rendering Performance
~~~~~~~~~~~~~~~~~~~~~

**Modern OpenGL**:
* Use VAOs for efficient rendering
* Minimize state changes
* Use instanced rendering for repeated objects
* Implement frustum culling

**Legacy OpenGL**:
* Use VBOs when available
* Minimize immediate mode calls
* Batch similar operations
* Use display lists for static geometry

**Example**:

.. code-block:: python

   # Efficient rendering
   def render_scene(self):
       # Set up state once
       glEnable(GL_DEPTH_TEST)
       glEnable(GL_CULL_FACE)
       
       # Render all objects with same state
       for obj in self.objects:
           if obj.visible:
               obj.render()
       
       # Clean up state
       glDisable(GL_CULL_FACE)
       glDisable(GL_DEPTH_TEST)

Memory Management
~~~~~~~~~~~~~~~~~

**Buffer Management**:
* Upload data once and reuse
* Delete unused buffers
* Use appropriate buffer types
* Monitor memory usage

**Example**:

.. code-block:: python

   class MeshManager:
       def __init__(self):
           self.meshes = {}
           self.buffers = {}
       
       def load_mesh(self, name, data):
           if name not in self.meshes:
               # Create new mesh
               mesh = self.create_mesh(data)
               self.meshes[name] = mesh
               self.buffers[name] = mesh.get_buffers()
           return self.meshes[name]
       
       def cleanup(self):
           for buffers in self.buffers.values():
               for buffer in buffers:
                   buffer.delete()
           self.buffers.clear()
           self.meshes.clear()

Debugging
---------

OpenGL Debugging
~~~~~~~~~~~~~~~~

**Error Checking**:

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

**Debug Output**:

.. code-block:: python

   def debug_print_gl_info():
       print(f"OpenGL version: {glGetString(GL_VERSION)}")
       print(f"Vendor: {glGetString(GL_VENDOR)}")
       print(f"Renderer: {glGetString(GL_RENDERER)}")
       print(f"Extensions: {glGetString(GL_EXTENSIONS)}")

**Performance Profiling**:

.. code-block:: python

   import time
   
   def profile_render():
       start_time = time.time()
       
       # Render scene
       self.render_scene()
       
       end_time = time.time()
       frame_time = end_time - start_time
       fps = 1.0 / frame_time
       
       print(f"Frame time: {frame_time:.3f}s, FPS: {fps:.1f}")

Common Issues
-------------

**OpenGL Context Issues**:
* Ensure OpenGL context is created before use
* Check for context loss
* Handle context recreation

**Memory Issues**:
* Monitor buffer usage
* Clean up unused resources
* Use appropriate data types

**Performance Issues**:
* Profile rendering code
* Optimize draw calls
* Use appropriate rendering techniques

**Cross-platform Issues**:
* Test on multiple platforms
* Handle platform-specific differences
* Use fallback implementations

For more information, see the :doc:`troubleshooting` guide.
