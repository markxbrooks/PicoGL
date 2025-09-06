Testing
=======

PicoGL includes a comprehensive testing framework to ensure reliability and compatibility across different platforms and OpenGL versions.

Test Structure
--------------

The test suite is organized as follows:

.. code-block:: text

   tests/
   ├── test_vertex_array_object.py      # VAO tests
   ├── test_vertex_buffer_group.py      # Legacy VBO tests
   ├── test_meshdata.py                 # MeshData tests
   ├── test_glmesh.py                   # Modern GLMesh tests
   ├── test_legacy_glmesh.py            # Legacy GLMesh tests
   ├── test_object_renderer.py          # ObjectRenderer tests
   └── test_texture_renderer.py         # TextureRenderer tests

Running Tests
-------------

Basic Test Execution
~~~~~~~~~~~~~~~~~~~~

**Run all tests**:
.. code-block:: bash

   python -m unittest discover tests

**Run specific test file**:
.. code-block:: bash

   python -m unittest tests.test_vertex_array_object

**Run specific test method**:
.. code-block:: bash

   python -m unittest tests.test_vertex_array_object.TestVertexArrayObject.test_initialization

**Run with verbose output**:
.. code-block:: bash

   python -m unittest discover tests -v

Using pytest
~~~~~~~~~~~~

**Install pytest**:
.. code-block:: bash

   pip install pytest pytest-cov

**Run tests with pytest**:
.. code-block:: bash

   pytest tests/

**Run with coverage**:
.. code-block:: bash

   pytest tests/ --cov=picogl

**Run specific test**:
.. code-block:: bash

   pytest tests/test_vertex_array_object.py::TestVertexArrayObject::test_initialization

Test Categories
---------------

Unit Tests
~~~~~~~~~~

Unit tests verify individual components in isolation:

**VertexArrayObject Tests**:
.. code-block:: python

   class TestVertexArrayObject(unittest.TestCase):
       def test_initialization(self):
           vao = VertexArrayObject()
           self.assertIsNotNone(vao)
       
       def test_add_vbo(self):
           vao = VertexArrayObject()
           vao.add_vbo(index=0, data=vertices, size=3)
           self.assertEqual(len(vao.vbos), 1)
       
       def test_add_ebo(self):
           vao = VertexArrayObject()
           vao.add_ebo(data=indices)
           self.assertIsNotNone(vao.ebo)

**MeshData Tests**:
.. code-block:: python

   class TestMeshData(unittest.TestCase):
       def test_from_raw(self):
           data = MeshData.from_raw(vertices=vertices, colors=colors)
           self.assertIsNotNone(data)
           self.assertEqual(data.vertex_count, len(vertices) // 3)
       
       def test_draw(self):
           data = MeshData.from_raw(vertices=vertices, colors=colors)
           data.draw()  # Should not raise exception

Integration Tests
~~~~~~~~~~~~~~~~~

Integration tests verify component interactions:

**Renderer Integration**:
.. code-block:: python

   class TestRendererIntegration(unittest.TestCase):
       def test_object_renderer_initialization(self):
           context = GLContext()
           data = MeshData.from_raw(vertices=vertices, colors=colors)
           renderer = ObjectRenderer(context=context, data=data)
           renderer.initialize()
           self.assertTrue(renderer.initialized)
       
       def test_texture_renderer_initialization(self):
           context = GLContext()
           data = MeshData.from_raw(vertices=vertices, uvs=uvs)
           renderer = TextureRenderer(context=context, data=data)
           renderer.initialize_textures()
           self.assertIsNotNone(renderer.texture)

Performance Tests
~~~~~~~~~~~~~~~~~

Performance tests verify rendering performance:

**Rendering Performance**:
.. code-block:: python

   class TestRenderingPerformance(unittest.TestCase):
       def test_render_performance(self):
           start_time = time.time()
           for _ in range(1000):
               renderer.render()
           end_time = time.time()
           frame_time = (end_time - start_time) / 1000
           self.assertLess(frame_time, 0.016)  # 60 FPS
       
       def test_memory_usage(self):
           initial_memory = psutil.Process().memory_info().rss
           # Create and use renderer
           renderer = create_renderer()
           renderer.render()
           final_memory = psutil.Process().memory_info().rss
           memory_increase = final_memory - initial_memory
           self.assertLess(memory_increase, 100 * 1024 * 1024)  # 100MB

Compatibility Tests
~~~~~~~~~~~~~~~~~~~

Compatibility tests verify cross-platform functionality:

**OpenGL Version Compatibility**:
.. code-block:: python

   class TestOpenGLCompatibility(unittest.TestCase):
       def test_modern_opengl(self):
           if has_modern_opengl():
               vao = VertexArrayObject()
               self.assertIsNotNone(vao)
       
       def test_legacy_opengl(self):
           if has_legacy_opengl():
               vbg = VertexBufferGroup()
               self.assertIsNotNone(vbg)
       
       def test_immediate_mode(self):
           # Test immediate mode fallback
           pass

Test Mocking
------------

OpenGL Mocking
~~~~~~~~~~~~~~

Since OpenGL requires a graphics context, tests use mocking:

**Global OpenGL Mocking**:
.. code-block:: python

   class TestVertexArrayObject(unittest.TestCase):
       def setUp(self):
           # Mock all OpenGL functions
           self.gl_patches = [
               patch('picogl.backend.modern.core.vertex.array.object.glGenVertexArrays'),
               patch('picogl.backend.modern.core.vertex.array.object.glBindVertexArray'),
               patch('picogl.backend.modern.core.vertex.array.object.glDeleteVertexArrays'),
               # ... more patches
           ]
           for patch_obj in self.gl_patches:
               patch_obj.start()
       
       def tearDown(self):
           for patch_obj in self.gl_patches:
               patch_obj.stop()

**Specific Function Mocking**:
.. code-block:: python

   def test_error_handling(self):
       with patch('picogl.backend.modern.core.vertex.array.object.glGenVertexArrays') as mock_gen:
           mock_gen.side_effect = OpenGLError("Context not available")
           with self.assertRaises(OpenGLError):
               VertexArrayObject()

Dependency Mocking
~~~~~~~~~~~~~~~~~~

Mock external dependencies:

**NumPy Mocking**:
.. code-block:: python

   @patch('numpy.array')
   def test_array_creation(self, mock_array):
       mock_array.return_value = np.array([1, 2, 3])
       result = create_vertex_array()
       mock_array.assert_called_once()

**PIL Mocking**:
.. code-block:: python

   @patch('PIL.Image.open')
   def test_texture_loading(self, mock_open):
       mock_image = MagicMock()
       mock_open.return_value = mock_image
       texture = load_texture("test.png")
       mock_open.assert_called_once_with("test.png")

Test Data
---------

Test Fixtures
~~~~~~~~~~~~~

Create reusable test data:

**Vertex Data**:
.. code-block:: python

   class TestData:
       @staticmethod
       def create_triangle_vertices():
           return np.array([
               [0, 0, 0],
               [1, 0, 0],
               [0, 1, 0]
           ], dtype=np.float32)
       
       @staticmethod
       def create_triangle_colors():
           return np.array([
               [1, 0, 0],
               [0, 1, 0],
               [0, 0, 1]
           ], dtype=np.float32)
       
       @staticmethod
       def create_triangle_faces():
           return np.array([
               [0, 1, 2]
           ], dtype=np.uint32)

**Mock Objects**:
.. code-block:: python

   class MockGLContext:
       def __init__(self):
           self.vaos = {}
           self.shader = MagicMock()
           self.mvp_matrix = np.identity(4, dtype=np.float32)
       
       def create_shader_program(self, vertex_file, fragment_file):
           self.shader = MagicMock()
           return self.shader

Test Utilities
~~~~~~~~~~~~~~

Create helper functions for testing:

**OpenGL Context Testing**:
.. code-block:: python

   def create_mock_opengl_context():
       """Create a mock OpenGL context for testing."""
       with patch('OpenGL.GL.glGetString') as mock_get_string:
           mock_get_string.return_value = b"OpenGL 3.3.0"
           return mock_get_string

**Error Testing**:
.. code-block:: python

   def test_with_gl_error(error_code, expected_exception):
       """Test function with specific OpenGL error."""
       with patch('OpenGL.GL.glGetError') as mock_get_error:
           mock_get_error.return_value = error_code
           with pytest.raises(expected_exception):
               function_that_uses_opengl()

Continuous Integration
----------------------

GitHub Actions
~~~~~~~~~~~~~~

**Test Workflow**:
.. code-block:: yaml

   name: Tests
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ${{ matrix.os }}
       strategy:
         matrix:
           os: [ubuntu-latest, windows-latest, macos-latest]
           python-version: [3.7, 3.8, 3.9, '3.10', '3.11']
       
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install dependencies
         run: |
           pip install -e .[dev]
       
       - name: Run tests
         run: |
           python -m unittest discover tests
       
       - name: Run coverage
         run: |
           pytest tests/ --cov=picogl --cov-report=xml
       
       - name: Upload coverage
         uses: codecov/codecov-action@v1

**Build Workflow**:
.. code-block:: yaml

   name: Build
   on: [push, release]
   
   jobs:
     build:
       runs-on: ${{ matrix.os }}
       strategy:
         matrix:
           os: [ubuntu-latest, windows-latest, macos-latest]
       
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.9'
       
       - name: Install dependencies
         run: |
           pip install build twine
       
       - name: Build package
         run: |
           python -m build
       
       - name: Upload artifacts
         uses: actions/upload-artifact@v2
         with:
           name: dist
           path: dist/

Test Coverage
-------------

Coverage Requirements
~~~~~~~~~~~~~~~~~~~~~

**Minimum Coverage**:
* Overall: 80%
* Critical modules: 90%
* New code: 95%

**Coverage Exclusions**:
* Test files
* Example files
* Platform-specific code
* Fallback implementations

**Coverage Report**:
.. code-block:: bash

   pytest tests/ --cov=picogl --cov-report=html --cov-report=term

**Coverage Configuration**:
.. code-block:: ini

   [coverage:run]
   source = picogl
   omit = 
       */tests/*
       */examples/*
       */__pycache__/*
       */legacy/*
   
   [coverage:report]
   exclude_lines =
       pragma: no cover
       def __repr__
       raise AssertionError
       raise NotImplementedError

Code Quality
------------

Linting
~~~~~~~

**flake8 Configuration**:
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

**Run Linting**:
.. code-block:: bash

   flake8 picogl/
   flake8 tests/

Type Checking
~~~~~~~~~~~~~

**mypy Configuration**:
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

**Run Type Checking**:
.. code-block:: bash

   mypy picogl/
   mypy tests/

Formatting
~~~~~~~~~~

**black Configuration**:
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

**Run Formatting**:
.. code-block:: bash

   black picogl/
   black tests/

Test Best Practices
-------------------

Writing Tests
~~~~~~~~~~~~~

**Test Naming**:
.. code-block:: python

   def test_initialization_with_valid_data(self):
       """Test initialization with valid input data."""
       pass
   
   def test_initialization_raises_error_with_invalid_data(self):
       """Test initialization raises error with invalid data."""
       pass

**Test Structure**:
.. code-block:: python

   def test_functionality(self):
       # Arrange
       input_data = create_test_data()
       expected_result = create_expected_result()
       
       # Act
       actual_result = function_under_test(input_data)
       
       # Assert
       self.assertEqual(actual_result, expected_result)

**Test Documentation**:
.. code-block:: python

   def test_complex_functionality(self):
       """Test complex functionality with multiple inputs.
       
       This test verifies that the function handles:
       - Valid input data
       - Edge cases
       - Error conditions
       
       Expected behavior:
       - Returns correct result for valid input
       - Handles edge cases gracefully
       - Raises appropriate errors for invalid input
       """
       pass

Test Maintenance
~~~~~~~~~~~~~~~~

**Keep Tests Simple**:
* One assertion per test
* Clear test names
* Minimal setup

**Avoid Test Dependencies**:
* Tests should be independent
* No shared state
* Clean up after tests

**Regular Test Updates**:
* Update tests when code changes
* Remove obsolete tests
* Add tests for new features

**Test Performance**:
* Keep tests fast
* Use mocking to avoid slow operations
* Parallel test execution when possible

Debugging Tests
~~~~~~~~~~~~~~~

**Verbose Output**:
.. code-block:: bash

   python -m unittest discover tests -v

**Debug Specific Test**:
.. code-block:: python

   import pdb
   
   def test_debugging(self):
       pdb.set_trace()  # Set breakpoint
       # Test code here

**Test Isolation**:
.. code-block:: python

   def test_isolated(self):
       # Use fresh instances
       context = GLContext()
       data = MeshData.from_raw(vertices=vertices, colors=colors)
       # Test without side effects

For more information about testing, see the :doc:`development` guide.
