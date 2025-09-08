Renderer API
============

The renderer module provides the core rendering functionality for PicoGL, including mesh data management, OpenGL context handling, and various renderer implementations.

Core Classes
------------

MeshData
~~~~~~~~

.. autoclass:: picogl.renderer.meshdata.MeshData
   :members:
   :undoc-members:
   :show-inheritance:

The ``MeshData`` class is the central data structure for storing 3D mesh information including vertices, colors, normals, and texture coordinates.

**Example**:

.. code-block:: python

   from picogl.renderer import MeshData
   import numpy as np
   
   # Create mesh data
   vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
   colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
   
   data = MeshData.from_raw(vertices=vertices, colors=colors)

GLContext
~~~~~~~~~

.. autoclass:: picogl.renderer.glcontext.GLContext
   :members:
   :undoc-members:
   :show-inheritance:

The ``GLContext`` class manages OpenGL-related state including VAOs, shaders, textures, and transformation matrices.

**Example**:

.. code-block:: python

   from picogl.renderer import GLContext
   
   # Create OpenGL context
   context = GLContext()
   
   # Create shader program
   context.create_shader_program(
       vertex_source_file="vertex.glsl",
       fragment_source_file="fragment.glsl"
   )

Renderer Classes
----------------

ObjectRenderer
~~~~~~~~~~~~~~

.. autoclass:: picogl.renderer.object.ObjectRenderer
   :members:
   :undoc-members:
   :show-inheritance:

The ``ObjectRenderer`` class provides unified rendering for both textured and untextured objects using modern OpenGL.

**Example**:

.. code-block:: python

   from picogl.renderer import GLContext, MeshData
   from picogl.renderer.object import ObjectRenderer
   
   # Create renderer
   context = GLContext()
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   renderer = ObjectRenderer(
       context=context,
       data=data,
       use_texture=False
   )
   
   # Initialize and render
   renderer.initialize_shaders()
   renderer.initialize()
   renderer.render()

TextureRenderer
~~~~~~~~~~~~~~~

.. autoclass:: picogl.renderer.texture.TextureRenderer
   :members:
   :undoc-members:
   :show-inheritance:

The ``TextureRenderer`` class extends ``ObjectRenderer`` to provide specialized texture rendering capabilities.

**Example**:

.. code-block:: python

   from picogl.renderer.texture import TextureRenderer
   
   # Create texture renderer
   renderer = TextureRenderer(
       context=context,
       data=data,
       base_dir="path/to/resources",
       use_texture=True,
       texture_file="texture.png"
   )
   
   # Initialize textures
   renderer.initialize_textures()

LegacyGLMesh
~~~~~~~~~~~~

.. autoclass:: picogl.renderer.legacy_glmesh.LegacyGLMesh
   :members:
   :undoc-members:
   :show-inheritance:

The ``LegacyGLMesh`` class provides OpenGL 1.x/2.x compatible mesh rendering for systems without modern OpenGL support.

**Example**:

.. code-block:: python

   from picogl.renderer.legacy_glmesh import LegacyGLMesh
   
   # Create legacy mesh
   mesh = LegacyGLMesh(
       vertices=vertices,
       faces=faces,
       colors=colors,
       normals=normals
   )
   
   # Upload to GPU and draw
   mesh.upload()
   mesh.draw()

GLMesh
~~~~~~

.. autoclass:: picogl.renderer.glmesh.GLMesh
   :members:
   :undoc-members:
   :show-inheritance:

The ``GLMesh`` class provides modern OpenGL mesh rendering with VAO/VBO support.

**Example**:

.. code-block:: python

   from picogl.renderer.glmesh import GLMesh
   
   # Create modern mesh
   mesh = GLMesh(
       vertices=vertices,
       faces=faces,
       colors=colors,
       normals=normals
   )
   
   # Upload to GPU and draw
   mesh.upload()
   mesh.draw()

Base Classes
------------

RendererBase
~~~~~~~~~~~~

.. autoclass:: picogl.renderer.base.RendererBase
   :members:
   :undoc-members:
   :show-inheritance:

The ``RendererBase`` class provides the base functionality for all renderers in PicoGL.

AbstractRenderer
~~~~~~~~~~~~~~~~

.. autoclass:: picogl.renderer.abstract.AbstractRenderer
   :members:
   :undoc-members:
   :show-inheritance:

The ``AbstractRenderer`` class defines the interface that all renderers must implement.

Utility Classes
---------------

UvRenderer
~~~~~~~~~~

.. autoclass:: picogl.renderer.uvrenderer.UvRenderer
   :members:
   :undoc-members:
   :show-inheritance:

The ``UvRenderer`` class provides 2D UV coordinate rendering for texture visualization.

**Example**:

.. code-block:: python

   from picogl.renderer.uvrenderer import UvRenderer
   
   # Create UV renderer
   renderer = UvRenderer()
   
   # Initialize with UV data
   renderer.initialize(uv_buffer, indices_buffer, index_count)
   renderer.render()

Data Structures
---------------

The renderer module uses several data structures to represent 3D mesh information:

**Vertices**: 3D positions of mesh vertices
**Colors**: RGB color values for each vertex
**Normals**: Surface normal vectors for lighting
**UVs**: Texture coordinates for texture mapping
**Faces**: Triangle indices defining mesh topology

**Example**:

.. code-block:: python

   # Vertex data (N, 3) array
   vertices = np.array([
       [0, 0, 0],  # Vertex 0
       [1, 0, 0],  # Vertex 1
       [0, 1, 0]   # Vertex 2
   ], dtype=np.float32)
   
   # Color data (N, 3) array
   colors = np.array([
       [1, 0, 0],  # Red
       [0, 1, 0],  # Green
       [0, 0, 1]   # Blue
   ], dtype=np.float32)
   
   # Face data (M, 3) array
   faces = np.array([
       [0, 1, 2]   # Triangle connecting vertices 0, 1, 2
   ], dtype=np.uint32)

Rendering Pipeline
------------------

The PicoGL rendering pipeline follows these steps:

1. **Data Preparation**: Create MeshData with vertices, colors, normals, etc.
2. **Context Setup**: Initialize GLContext with shaders and OpenGL state
3. **Renderer Creation**: Create appropriate renderer (ObjectRenderer, TextureRenderer, etc.)
4. **Initialization**: Call renderer.initialize() to set up OpenGL resources
5. **Rendering**: Call renderer.render() to draw the mesh

**Example**:

.. code-block:: python

   # 1. Prepare data
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   # 2. Setup context
   context = GLContext()
   context.create_shader_program("vertex.glsl", "fragment.glsl")
   
   # 3. Create renderer
   renderer = ObjectRenderer(context=context, data=data)
   
   # 4. Initialize
   renderer.initialize_shaders()
   renderer.initialize()
   
   # 5. Render (in main loop)
   renderer.render()

Error Handling
--------------

PicoGL renderers include comprehensive error handling:

**OpenGL Context Errors**: Fallback to legacy rendering
**Shader Compilation Errors**: Use fallback shaders
**Texture Loading Errors**: Skip texture rendering
**Mesh Upload Errors**: Use immediate mode rendering

**Example**:

.. code-block:: python

   try:
       renderer.initialize()
   except OpenGLError as e:
       print(f"OpenGL error: {e}")
       # Fallback to legacy rendering
   except Exception as e:
       print(f"Unexpected error: {e}")
       # Handle gracefully

Performance Considerations
-------------------------

**Modern Renderers** (ObjectRenderer, TextureRenderer):
* Best performance with modern OpenGL
* Requires OpenGL 3.3+ support
* Uses VAO/VBO for efficient rendering
* Supports advanced features

**Legacy Renderers** (LegacyGLMesh):
* Compatible with older OpenGL versions
* Uses immediate mode or legacy VBOs
* Good performance on older hardware
* Limited feature set

**Minimal Renderers** (Immediate mode):
* Maximum compatibility
* Uses glBegin/glEnd for rendering
* Lower performance but works everywhere
* No advanced features

Best Practices
--------------

1. **Choose the right renderer** for your target platform
2. **Use MeshData.from_raw()** for easy data creation
3. **Initialize renderers once** and reuse them
4. **Handle errors gracefully** with fallbacks
5. **Test on multiple platforms** for compatibility

**Example**:

.. code-block:: python

   # Choose renderer based on OpenGL support
   if has_modern_opengl():
       renderer = ObjectRenderer(context, data)
   elif has_legacy_opengl():
       renderer = LegacyGLMesh(vertices, faces, colors)
   else:
       # Use immediate mode fallback
       renderer = ImmediateModeRenderer(vertices, colors)
