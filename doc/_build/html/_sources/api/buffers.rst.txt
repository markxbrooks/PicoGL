Buffers API
===========

The buffers module provides OpenGL buffer management functionality for PicoGL, including vertex buffers, element buffers, and vertex array objects.

Core Classes
------------

VertexArrayObject
~~~~~~~~~~~~~~~~~

.. autoclass:: picogl.backend.modern.core.vertex.array.object.VertexArrayObject
   :members:
   :undoc-members:
   :show-inheritance:

The ``VertexArrayObject`` class manages OpenGL Vertex Array Objects (VAOs) for modern OpenGL rendering.

**Example**:

.. code-block:: python

   from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
   
   # Create VAO
   vao = VertexArrayObject()
   
   # Add vertex buffer
   vao.add_vbo(index=0, data=vertices, size=3)
   
   # Add color buffer
   vao.add_vbo(index=1, data=colors, size=3)
   
   # Add element buffer
   vao.add_ebo(data=indices)
   
   # Draw
   vao.draw(mode=GL_TRIANGLES, index_count=len(indices))

VertexBufferGroup
~~~~~~~~~~~~~~~~~

.. autoclass:: picogl.buffers.vertex.legacy.VertexBufferGroup
   :members:
   :undoc-members:
   :show-inheritance:

The ``VertexBufferGroup`` class provides legacy OpenGL buffer management for systems without VAO support.

**Example**:

.. code-block:: python

   from picogl.buffers.vertex.legacy import VertexBufferGroup
   
   # Create vertex buffer group
   vbg = VertexBufferGroup()
   
   # Add vertex buffer
   vbg.add_vbo("position", vertices, 3)
   
   # Add color buffer
   vbg.add_vbo("color", colors, 3)
   
   # Add element buffer
   vbg.add_ebo(indices)
   
   # Bind and draw
   vbg.bind()
   vbg.draw(mode=GL_TRIANGLES)

Buffer Classes
--------------

Modern Buffers
~~~~~~~~~~~~~~

ModernVBO
^^^^^^^^^

.. autoclass:: picogl.backend.modern.core.vertex.buffer.vertex.ModernVBO
   :members:
   :undoc-members:
   :show-inheritance:

ModernEBO
^^^^^^^^^

.. autoclass:: picogl.backend.modern.core.vertex.buffer.element.ModernEBO
   :members:
   :undoc-members:
   :show-inheritance:

Legacy Buffers
~~~~~~~~~~~~~~

LegacyVBO
^^^^^^^^^

.. autoclass:: picogl.backend.legacy.core.vertex.buffer.vertex.LegacyVBO
   :members:
   :undoc-members:
   :show-inheritance:

LegacyPositionVBO
^^^^^^^^^^^^^^^^^

.. autoclass:: picogl.backend.legacy.core.vertex.buffer.position.LegacyPositionVBO
   :members:
   :undoc-members:
   :show-inheritance:

LegacyColorVBO
^^^^^^^^^^^^^^

.. autoclass:: picogl.backend.legacy.core.vertex.buffer.color.LegacyColorVBO
   :members:
   :undoc-members:
   :show-inheritance:

LegacyNormalVBO
^^^^^^^^^^^^^^^

.. autoclass:: picogl.backend.legacy.core.vertex.buffer.normal.LegacyNormalVBO
   :members:
   :undoc-members:
   :show-inheritance:

LegacyEBO
^^^^^^^^^

.. autoclass:: picogl.backend.legacy.core.vertex.buffer.element.LegacyEBO
   :members:
   :undoc-members:
   :show-inheritance:

Base Classes
------------

VertexBase
~~~~~~~~~~

.. autoclass:: picogl.buffers.base.VertexBase
   :members:
   :undoc-members:
   :show-inheritance:

The ``VertexBase`` class provides the base functionality for all vertex buffer classes.

VertexBuffer
~~~~~~~~~~~~

.. autoclass:: picogl.buffers.vertex.modern.ModernVertexArrayGroup
   :members:
   :undoc-members:
   :show-inheritance:

The ``VertexBuffer`` class provides the base functionality for vertex buffer objects.

Data Structures
---------------

LayoutDescriptor
~~~~~~~~~~~~~~~~

.. autoclass:: picogl.buffers.factory.layout.LayoutDescriptor
   :members:
   :undoc-members:
   :show-inheritance:

The ``LayoutDescriptor`` class describes the layout of vertex attributes in a buffer.

**Example**:

.. code-block:: python

   from picogl.buffers.factory.layout import create_layout
   
   # Create layout descriptor
   layout = create_layout([
       AttributeSpec(name="position", size=3, type=GL_FLOAT),
       AttributeSpec(name="color", size=3, type=GL_FLOAT),
       AttributeSpec(name="normal", size=3, type=GL_FLOAT)
   ])

AttributeSpec
~~~~~~~~~~~~~

.. autoclass:: picogl.buffers.attributes.AttributeSpec
   :members:
   :undoc-members:
   :show-inheritance:

The ``AttributeSpec`` class describes a single vertex attribute.

**Example**:

.. code-block:: python

   from picogl.buffers.attributes import AttributeSpec
   
   # Create attribute specification
   position_attr = AttributeSpec(
       name="position",
       size=3,
       type=GL_FLOAT,
       normalized=False,
       stride=0,
       offset=0
   )

Buffer Management
-----------------

Creating Buffers
~~~~~~~~~~~~~~~~

**Modern OpenGL (VAO/VBO)**:

.. code-block:: python

   from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
   
   # Create VAO
   vao = VertexArrayObject()
   
   # Add vertex buffer
   vao.add_vbo(index=0, data=vertices, size=3)
   
   # Add color buffer
   vao.add_vbo(index=1, data=colors, size=3)
   
   # Add element buffer
   vao.add_ebo(data=indices)

**Legacy OpenGL (VBO only)**:

.. code-block:: python

   from picogl.buffers.vertex.legacy import VertexBufferGroup
   
   # Create vertex buffer group
   vbg = VertexBufferGroup()
   
   # Add vertex buffer
   vbg.add_vbo("position", vertices, 3)
   
   # Add color buffer
   vbg.add_vbo("color", colors, 3)
   
   # Add element buffer
   vbg.add_ebo(indices)

Binding Buffers
~~~~~~~~~~~~~~~

**Modern OpenGL**:

.. code-block:: python

   # Bind VAO (automatically binds all VBOs)
   with vao:
       # Draw calls here
       vao.draw(mode=GL_TRIANGLES, index_count=len(indices))

**Legacy OpenGL**:

.. code-block:: python

   # Bind vertex buffer group
   vbg.bind()
   
   # Draw calls here
   vbg.draw(mode=GL_TRIANGLES)
   
   # Unbind
   vbg.unbind()

Buffer Types
------------

Vertex Buffers
~~~~~~~~~~~~~~

Vertex buffers store vertex data such as positions, colors, normals, and texture coordinates.

**Position Buffer**:

.. code-block:: python

   # 3D positions (N, 3) array
   vertices = np.array([
       [0, 0, 0],  # Vertex 0
       [1, 0, 0],  # Vertex 1
       [0, 1, 0]   # Vertex 2
   ], dtype=np.float32)

**Color Buffer**:

.. code-block:: python

   # RGB colors (N, 3) array
   colors = np.array([
       [1, 0, 0],  # Red
       [0, 1, 0],  # Green
       [0, 0, 1]   # Blue
   ], dtype=np.float32)

**Normal Buffer**:

.. code-block:: python

   # Surface normals (N, 3) array
   normals = np.array([
       [0, 0, 1],  # Normal 0
       [0, 0, 1],  # Normal 1
       [0, 0, 1]   # Normal 2
   ], dtype=np.float32)

**UV Buffer**:

.. code-block:: python

   # Texture coordinates (N, 2) array
   uvs = np.array([
       [0, 0],  # UV 0
       [1, 0],  # UV 1
       [0, 1]   # UV 2
   ], dtype=np.float32)

Element Buffers
~~~~~~~~~~~~~~~

Element buffers store indices that define the topology of the mesh.

**Element Buffer**:

.. code-block:: python

   # Triangle indices (M, 3) array
   indices = np.array([
       [0, 1, 2]  # Triangle connecting vertices 0, 1, 2
   ], dtype=np.uint32)

Buffer Operations
-----------------

Uploading Data
~~~~~~~~~~~~~~

**Modern OpenGL**:

.. code-block:: python

   # Upload vertex data
   vao.add_vbo(index=0, data=vertices, size=3)
   
   # Upload color data
   vao.add_vbo(index=1, data=colors, size=3)
   
   # Upload element data
   vao.add_ebo(data=indices)

**Legacy OpenGL**:

.. code-block:: python

   # Upload vertex data
   vbg.add_vbo("position", vertices, 3)
   
   # Upload color data
   vbg.add_vbo("color", colors, 3)
   
   # Upload element data
   vbg.add_ebo(indices)

Drawing
~~~~~~~

**Modern OpenGL**:

.. code-block:: python

   # Draw with VAO
   with vao:
       vao.draw(mode=GL_TRIANGLES, index_count=len(indices))

**Legacy OpenGL**:

.. code-block:: python

   # Draw with vertex buffer group
   vbg.bind()
   vbg.draw(mode=GL_TRIANGLES)
   vbg.unbind()

Cleanup
~~~~~~~

**Modern OpenGL**:

.. code-block:: python

   # Cleanup VAO
   vao.delete()

**Legacy OpenGL**:

.. code-block:: python

   # Cleanup vertex buffer group
   vbg.delete()

Error Handling
--------------

Buffer operations include comprehensive error handling:

**OpenGL Context Errors**: Check for valid OpenGL context
**Buffer Creation Errors**: Handle OpenGL buffer creation failures
**Data Upload Errors**: Validate data before uploading
**Drawing Errors**: Handle OpenGL drawing failures

**Example**:

.. code-block:: python

   try:
       vao.add_vbo(index=0, data=vertices, size=3)
   except OpenGLError as e:
       print(f"OpenGL error: {e}")
       # Handle gracefully
   except ValueError as e:
       print(f"Data error: {e}")
       # Validate data
   except Exception as e:
       print(f"Unexpected error: {e}")
       # Handle gracefully

Performance Considerations
-------------------------

**Modern Buffers (VAO/VBO)**:
* Best performance with modern OpenGL
* Efficient GPU memory usage
* Fast drawing operations
* Requires OpenGL 3.0+ support

**Legacy Buffers (VBO only)**:
* Compatible with older OpenGL versions
* Good performance on older hardware
* Uses client state management
* Limited feature set

**Immediate Mode**:
* Maximum compatibility
* Uses glBegin/glEnd for rendering
* Lower performance but works everywhere
* No buffer management

Best Practices
--------------

1. **Use appropriate buffer type** for your target platform
2. **Upload data once** and reuse buffers
3. **Use VAOs** for modern OpenGL when possible
4. **Handle errors gracefully** with fallbacks
5. **Clean up resources** when done

**Example**:

.. code-block:: python

   # Choose buffer type based on OpenGL support
   if has_modern_opengl():
       vao = VertexArrayObject()
       vao.add_vbo(index=0, data=vertices, size=3)
   elif has_legacy_opengl():
       vbg = VertexBufferGroup()
       vbg.add_vbo("position", vertices, 3)
   else:
       # Use immediate mode fallback
       pass
