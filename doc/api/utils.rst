Utils API
=========

The utils module provides utility functionality for PicoGL, including data loading, texture management, and helper functions.

Core Classes
------------

ObjectLoader
~~~~~~~~~~~~

.. autoclass:: picogl.utils.loader.object.ObjectLoader
   :members:
   :undoc-members:
   :show-inheritance:

The ``ObjectLoader`` class provides functionality for loading 3D object files (OBJ format).

**Example**:

.. code-block:: python

   from picogl.utils.loader.object import ObjectLoader
   
   # Load OBJ file
   loader = ObjectLoader("model.obj")
   data = loader.to_array_style()
   
   # Create mesh data
   from picogl.renderer import MeshData
   mesh_data = MeshData.from_raw(
       vertices=data.vertices,
       normals=data.normals,
       colors=data.colors
   )

TextureLoader
~~~~~~~~~~~~~

.. autoclass:: picogl.utils.loader.texture.TextureLoader
   :members:
   :undoc-members:
   :show-inheritance:

The ``TextureLoader`` class provides functionality for loading and managing textures.

**Example**:

.. code-block:: python

   from picogl.utils.loader.texture import TextureLoader
   
   # Load texture
   loader = TextureLoader("texture.png")
   texture = loader.load()
   
   # Use texture
   texture.bind()
   # Draw textured geometry

Helper Functions
----------------

GL Initialization
~~~~~~~~~~~~~~~~~

.. autofunction:: picogl.utils.gl_init.execute_gl_tasks

Executes a list of OpenGL initialization tasks.

**Example**:

.. code-block:: python

   from picogl.utils.gl_init import execute_gl_tasks, init_gl_list
   
   # Execute initialization tasks
   execute_gl_tasks(init_gl_list)

.. autofunction:: picogl.utils.gl_init.init_gl_list

Returns a list of OpenGL initialization tasks.

**Example**:

.. code-block:: python

   from picogl.utils.gl_init import init_gl_list
   
   # Get initialization tasks
   tasks = init_gl_list
   execute_gl_tasks(tasks)

.. autofunction:: picogl.utils.gl_init.paint_gl_list

Returns a list of OpenGL painting tasks.

**Example**:

.. code-block:: python

   from picogl.utils.gl_init import paint_gl_list
   
   # Get painting tasks
   tasks = paint_gl_list
   execute_gl_tasks(tasks)

Texture Utilities
~~~~~~~~~~~~~~~~~

.. autofunction:: picogl.utils.texture.bind_texture_array

Binds a texture array to the specified texture unit.

**Example**:

.. code-block:: python

   from picogl.utils.texture import bind_texture_array
   
   # Bind texture to unit 0
   bind_texture_array(texture_id, 0)

Normal Generation
~~~~~~~~~~~~~~~~~

.. autofunction:: picogl.utils.normal.compute_vertex_normals

Generates surface normals for a mesh.

**Example**:

.. code-block:: python

   from picogl.utils.normal import compute_vertex_normals
   
   # Generate normals
   normals = compute_vertex_normals(vertices, faces)

Reshape Utilities
~~~~~~~~~~~~~~~~~

.. autofunction:: picogl.utils.reshape.float32_row

Reshapes input to a single row and converts to np.float32.

**Example**:

.. code-block:: python

   from picogl.utils.reshape import float32_row
   
   # Reshape data
   data = float32_row([1, 2, 3, 4, 5])

Data Loading
------------

OBJ File Loading
~~~~~~~~~~~~~~~

**Basic Loading**:

.. code-block:: python

   from picogl.utils.loader.object import ObjectLoader
   
   # Load OBJ file
   loader = ObjectLoader("model.obj")
   data = loader.to_array_style()
   
   # Access data
   vertices = data.vertices
   normals = data.normals
   colors = data.colors
   uvs = data.uvs

**Advanced Loading**:

.. code-block:: python

   # Load with options
   loader = ObjectLoader("model.obj")
   loader.set_options(
       normalize=True,
       compute_normals=True,
       generate_colors=True
   )
   
   data = loader.to_array_style()

**Error Handling**:

.. code-block:: python

   try:
       loader = ObjectLoader("model.obj")
       data = loader.to_array_style()
   except FileNotFoundError:
       print("OBJ file not found")
   except ValueError as e:
       print(f"Invalid OBJ file: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Texture Loading
~~~~~~~~~~~~~~~

**Basic Loading**:

.. code-block:: python

   from picogl.utils.loader.texture import TextureLoader
   
   # Load texture
   loader = TextureLoader("texture.png")
   texture = loader.load()
   
   # Use texture
   texture.bind()

**Advanced Loading**:

.. code-block:: python

   # Load with options
   loader = TextureLoader("texture.png")
   loader.set_options(
       flip_vertical=True,
       generate_mipmaps=True,
       wrap_mode=GL_REPEAT
   )
   
   texture = loader.load()

**Error Handling**:

.. code-block:: python

   try:
       loader = TextureLoader("texture.png")
       texture = loader.load()
   except FileNotFoundError:
       print("Texture file not found")
   except ValueError as e:
       print(f"Invalid texture file: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Data Processing
---------------

Mesh Data Processing
~~~~~~~~~~~~~~~~~~~~

**Vertex Processing**:

.. code-block:: python

   import numpy as np
   
   # Normalize vertices
   vertices = vertices / np.linalg.norm(vertices, axis=1, keepdims=True)
   
   # Center vertices
   center = np.mean(vertices, axis=0)
   vertices = vertices - center
   
   # Scale vertices
   scale = 1.0 / np.max(np.abs(vertices))
   vertices = vertices * scale

**Normal Processing**:

.. code-block:: python

   from picogl.utils.normal import compute_vertex_normals
   
   # Generate normals
   normals = compute_vertex_normals(vertices, faces)
   
   # Normalize normals
   normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)

**Color Processing**:

.. code-block:: python

   # Generate colors based on normals
   colors = (normals + 1.0) / 2.0
   
   # Generate colors based on vertices
   colors = (vertices - vertices.min()) / (vertices.max() - vertices.min())
   
   # Generate random colors
   colors = np.random.rand(len(vertices), 3)

Texture Processing
~~~~~~~~~~~~~~~~~~

**UV Coordinate Processing**:

.. code-block:: python

   # Flip V coordinates
   uvs[:, 1] = 1.0 - uvs[:, 1]
   
   # Scale UV coordinates
   uvs = uvs * 2.0 - 1.0
   
   # Wrap UV coordinates
   uvs = uvs % 1.0

**Texture Format Conversion**:

.. code-block:: python

   from PIL import Image
   
   # Convert to RGBA
   image = Image.open("texture.png").convert("RGBA")
   
   # Convert to RGB
   image = Image.open("texture.png").convert("RGB")
   
   # Resize texture
   image = image.resize((512, 512))

File Management
---------------

Path Handling
~~~~~~~~~~~~~

**Path Operations**:

.. code-block:: python

   from pathlib import Path
   
   # Create path
   base_dir = Path("resources")
   texture_path = base_dir / "textures" / "texture.png"
   
   # Check if path exists
   if texture_path.exists():
       print("Texture file exists")
   
   # Get absolute path
   abs_path = texture_path.absolute()

**Resource Management**:

.. code-block:: python

   # Find resource files
   def find_resources(directory, pattern="*.obj"):
       return list(Path(directory).glob(pattern))
   
   # Load all OBJ files
   obj_files = find_resources("models", "*.obj")
   for obj_file in obj_files:
       loader = ObjectLoader(str(obj_file))
       data = loader.to_array_style()

Error Handling
--------------

Loading Errors
~~~~~~~~~~~~~~

**File Not Found**:

.. code-block:: python

   try:
       loader = ObjectLoader("nonexistent.obj")
       data = loader.to_array_style()
   except FileNotFoundError:
       print("File not found, using fallback")
       # Use fallback data
   except Exception as e:
       print(f"Unexpected error: {e}")

**Invalid File Format**:

.. code-block:: python

   try:
       loader = ObjectLoader("invalid.obj")
       data = loader.to_array_style()
   except ValueError as e:
       print(f"Invalid file format: {e}")
       # Handle gracefully
   except Exception as e:
       print(f"Unexpected error: {e}")

**Memory Errors**:

.. code-block:: python

   try:
       loader = ObjectLoader("large_model.obj")
       data = loader.to_array_style()
   except MemoryError:
       print("File too large, using simplified version")
       # Use simplified data
   except Exception as e:
       print(f"Unexpected error: {e}")

Performance Considerations
-------------------------

**Lazy Loading**:

.. code-block:: python

   class LazyLoader:
       def __init__(self, filename):
           self.filename = filename
           self._data = None
       
       @property
       def data(self):
           if self._data is None:
               self._data = self._load_data()
           return self._data
       
       def _load_data(self):
           loader = ObjectLoader(self.filename)
           return loader.to_array_style()

**Caching**:

.. code-block:: python

   import functools
   
   @functools.lru_cache(maxsize=128)
   def load_texture(filename):
       loader = TextureLoader(filename)
       return loader.load()

**Batch Loading**:

.. code-block:: python

   def load_multiple_objects(filenames):
       results = []
       for filename in filenames:
           try:
               loader = ObjectLoader(filename)
               data = loader.to_array_style()
               results.append(data)
           except Exception as e:
               print(f"Failed to load {filename}: {e}")
               results.append(None)
       return results

Best Practices
--------------

1. **Use appropriate loader** for your file type
2. **Handle errors gracefully** with fallbacks
3. **Cache loaded data** when possible
4. **Validate data** before using
5. **Use lazy loading** for large files

**Example**:

.. code-block:: python

   # Choose loader based on file type
   if filename.endswith('.obj'):
       loader = ObjectLoader(filename)
   elif filename.endswith(('.png', '.jpg', '.jpeg')):
       loader = TextureLoader(filename)
   else:
       raise ValueError(f"Unsupported file type: {filename}")
   
   # Load with error handling
   try:
       data = loader.load()
   except Exception as e:
       print(f"Failed to load {filename}: {e}")
       # Use fallback data
       data = create_fallback_data()
   
   return data
