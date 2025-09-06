Shaders API
===========

The shaders module provides OpenGL shader management functionality for PicoGL, including shader compilation, program creation, and uniform management.

Core Classes
------------

ShaderProgram
~~~~~~~~~~~~~

.. autoclass:: picogl.backend.modern.core.shader.program.ShaderProgram
   :members:
   :undoc-members:
   :show-inheritance:

The ``ShaderProgram`` class manages OpenGL shader programs, including vertex and fragment shaders.

**Example**:
.. code-block:: python

   from picogl.backend.modern.core.shader.program import ShaderProgram
   
   # Create shader program
   shader = ShaderProgram(
       vertex_source_file="vertex.glsl",
       fragment_source_file="fragment.glsl"
   )
   
   # Use shader
   with shader:
       shader.uniform("mvp_matrix", mvp_matrix)
       shader.uniform("color", [1.0, 0.0, 0.0])
       # Draw calls here

ShaderManager
~~~~~~~~~~~~~

.. autoclass:: picogl.shaders.manager.ShaderManager
   :members:
   :undoc-members:
   :show-inheritance:

The ``ShaderManager`` class provides centralized shader management for multiple shader programs.

**Example**:
.. code-block:: python

   from picogl.shaders.manager import ShaderManager
   
   # Create shader manager
   manager = ShaderManager(shader_directory="glsl/")
   
   # Load shaders
   manager.load_shader(ShaderType.BASIC, 1)
   manager.load_shader(ShaderType.TEXTURE, 2)
   
   # Use shader
   shader = manager.get(ShaderType.BASIC)
   with shader:
       # Draw calls here

Shader Types
------------

ShaderType
~~~~~~~~~~

.. autoclass:: picogl.shaders.type.ShaderType
   :members:
   :undoc-members:
   :show-inheritance:

The ``ShaderType`` enum defines the available shader types in PicoGL.

**Available Types**:
* ``BASIC``: Basic color shader
* ``TEXTURE``: Texture mapping shader
* ``LIGHTING``: Lighting and shading shader
* ``NORMAL_MAPPING``: Normal mapping shader
* ``TRANSPARENT``: Transparent rendering shader
* ``TEXT``: Text rendering shader

**Example**:
.. code-block:: python

   from picogl.shaders.type import ShaderType
   
   # Use shader type
   shader_type = ShaderType.BASIC
   shader = manager.get(shader_type)

Shader Compilation
------------------

Compile Shaders
~~~~~~~~~~~~~~~

.. autofunction:: picogl.shaders.compile.compile_shaders

Compiles vertex and fragment shader source code into OpenGL shaders.

**Example**:
.. code-block:: python

   from picogl.shaders.compile import compile_shaders
   
   # Compile shaders
   vertex_source = """
   #version 330 core
   layout(location = 0) in vec3 position;
   uniform mat4 mvp_matrix;
   void main() {
       gl_Position = mvp_matrix * vec4(position, 1.0);
   }
   """
   
   fragment_source = """
   #version 330 core
   out vec4 color;
   uniform vec3 color_uniform;
   void main() {
       color = vec4(color_uniform, 1.0);
   }
   """
   
   shader = compile_shaders(vertex_source, fragment_source, "basic")

Load Shaders
~~~~~~~~~~~~

.. autofunction:: picogl.shaders.load.load_fragment_and_vertex_for_shader_type

Loads vertex and fragment shader source code from files.

**Example**:
.. code-block:: python

   from picogl.shaders.load import load_fragment_and_vertex_for_shader_type
   
   # Load shader files
   vertex_src, fragment_src = load_fragment_and_vertex_for_shader_type(
       "basic", "glsl/"
   )
   
   # Compile shaders
   shader = compile_shaders(vertex_src, fragment_src, "basic")

Uniform Management
------------------

ShaderUniform
~~~~~~~~~~~~~

.. autoclass:: picogl.shaders.shader_uniform.ShaderUniform
   :members:
   :undoc-members:
   :show-inheritance:

The ``ShaderUniform`` class manages OpenGL shader uniforms.

**Example**:
.. code-block:: python

   from picogl.shaders.shader_uniform import ShaderUniform
   
   # Create uniform
   uniform = ShaderUniform(shader, "mvp_matrix")
   
   # Set uniform value
   uniform.set(mvp_matrix)

Uniform Types
~~~~~~~~~~~~~

PicoGL supports various uniform types:

**Matrix Uniforms**:
.. code-block:: python

   # 4x4 matrix
   shader.uniform("mvp_matrix", mvp_matrix)
   
   # 3x3 matrix
   shader.uniform("normal_matrix", normal_matrix)

**Vector Uniforms**:
.. code-block:: python

   # 3D vector
   shader.uniform("color", [1.0, 0.0, 0.0])
   
   # 4D vector
   shader.uniform("position", [0.0, 0.0, 0.0, 1.0])

**Scalar Uniforms**:
.. code-block:: python

   # Float
   shader.uniform("time", 0.5)
   
   # Integer
   shader.uniform("texture_sampler", 0)

**Boolean Uniforms**:
.. code-block:: python

   # Boolean
   shader.uniform("use_texture", True)

Built-in Shaders
----------------

PicoGL includes several built-in shader programs:

Basic Color Shader
~~~~~~~~~~~~~~~~~~

**Vertex Shader**:
.. code-block:: glsl

   #version 330 core
   layout(location = 0) in vec3 position;
   layout(location = 1) in vec3 color;
   
   uniform mat4 mvp_matrix;
   
   out vec3 fragment_color;
   
   void main() {
       gl_Position = mvp_matrix * vec4(position, 1.0);
       fragment_color = color;
   }

**Fragment Shader**:
.. code-block:: glsl

   #version 330 core
   in vec3 fragment_color;
   out vec4 color;
   
   void main() {
       color = vec4(fragment_color, 1.0);
   }

Texture Shader
~~~~~~~~~~~~~~

**Vertex Shader**:
.. code-block:: glsl

   #version 330 core
   layout(location = 0) in vec3 position;
   layout(location = 1) in vec2 uv;
   
   uniform mat4 mvp_matrix;
   
   out vec2 fragment_uv;
   
   void main() {
       gl_Position = mvp_matrix * vec4(position, 1.0);
       fragment_uv = uv;
   }

**Fragment Shader**:
.. code-block:: glsl

   #version 330 core
   in vec2 fragment_uv;
   
   uniform sampler2D texture0;
   
   out vec4 color;
   
   void main() {
       color = texture(texture0, fragment_uv);
   }

Lighting Shader
~~~~~~~~~~~~~~~

**Vertex Shader**:
.. code-block:: glsl

   #version 330 core
   layout(location = 0) in vec3 position;
   layout(location = 1) in vec3 normal;
   
   uniform mat4 mvp_matrix;
   uniform mat4 model_matrix;
   
   out vec3 frag_position;
   out vec3 frag_normal;
   
   void main() {
       gl_Position = mvp_matrix * vec4(position, 1.0);
       frag_position = vec3(model_matrix * vec4(position, 1.0));
       frag_normal = mat3(transpose(inverse(model_matrix))) * normal;
   }

**Fragment Shader**:
.. code-block:: glsl

   #version 330 core
   in vec3 frag_position;
   in vec3 frag_normal;
   
   uniform vec3 light_pos;
   uniform vec3 view_pos;
   uniform vec3 object_color;
   
   out vec4 color;
   
   void main() {
       vec3 norm = normalize(frag_normal);
       vec3 light_dir = normalize(light_pos - frag_position);
       
       float diff = max(dot(norm, light_dir), 0.0);
       vec3 diffuse = diff * object_color;
       
       vec3 ambient = 0.1 * object_color;
       vec3 result = ambient + diffuse;
       
       color = vec4(result, 1.0);
   }

Fallback Shaders
~~~~~~~~~~~~~~~~

PicoGL includes fallback shaders for systems with limited OpenGL support:

**Fallback Vertex Shader**:
.. code-block:: glsl

   #version 120
   attribute vec3 in_position;
   uniform mat4 mvp;
   
   void main() {
       gl_Position = mvp * vec4(in_position, 1.0);
   }

**Fallback Fragment Shader**:
.. code-block:: glsl

   #version 120
   void main() {
       gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);  // Hot pink
   }

Shader Usage
------------

Creating Shader Programs
~~~~~~~~~~~~~~~~~~~~~~~~

**From Files**:
.. code-block:: python

   from picogl.backend.modern.core.shader.program import ShaderProgram
   
   # Create shader from files
   shader = ShaderProgram(
       vertex_source_file="vertex.glsl",
       fragment_source_file="fragment.glsl",
       glsl_dir="glsl/"
   )

**From Source**:
.. code-block:: python

   # Create shader from source code
   shader = ShaderProgram(
       vertex_source=vertex_source,
       fragment_source=fragment_source
   )

Using Shaders
~~~~~~~~~~~~~

**Basic Usage**:
.. code-block:: python

   # Use shader
   with shader:
       shader.uniform("mvp_matrix", mvp_matrix)
       shader.uniform("color", [1.0, 0.0, 0.0])
       # Draw calls here

**Advanced Usage**:
.. code-block:: python

   # Bind shader
   shader.bind()
   
   # Set uniforms
   shader.uniform("mvp_matrix", mvp_matrix)
   shader.uniform("model_matrix", model_matrix)
   shader.uniform("view_pos", camera_position)
   
   # Draw
   mesh.draw()
   
   # Unbind shader
   shader.unbind()

Error Handling
--------------

Shader operations include comprehensive error handling:

**Compilation Errors**: Check shader source code
**Link Errors**: Check shader program compatibility
**Uniform Errors**: Validate uniform names and types
**Context Errors**: Check OpenGL context

**Example**:
.. code-block:: python

   try:
       shader = ShaderProgram(
           vertex_source_file="vertex.glsl",
           fragment_source_file="fragment.glsl"
       )
   except ShaderCompilationError as e:
       print(f"Shader compilation error: {e}")
       # Check shader source code
   except ShaderLinkError as e:
       print(f"Shader link error: {e}")
       # Check shader compatibility
   except Exception as e:
       print(f"Unexpected error: {e}")
       # Handle gracefully

Performance Considerations
-------------------------

**Modern Shaders (OpenGL 3.3+)**:
* Best performance and features
* Full shader pipeline support
* Advanced uniform types
* Requires modern OpenGL

**Legacy Shaders (OpenGL 1.x/2.x)**:
* Compatible with older OpenGL versions
* Limited shader features
* Uses fixed function pipeline
* Good performance on older hardware

**Fallback Shaders**:
* Maximum compatibility
* Basic functionality only
* Uses immediate mode rendering
* Works on any OpenGL system

Best Practices
--------------

1. **Use appropriate shader type** for your target platform
2. **Compile shaders once** and reuse them
3. **Handle compilation errors** gracefully
4. **Use fallback shaders** for compatibility
5. **Test on multiple platforms** for compatibility

**Example**:
.. code-block:: python

   # Choose shader based on OpenGL support
   if has_modern_opengl():
       shader = ShaderProgram(
           vertex_source_file="vertex.glsl",
           fragment_source_file="fragment.glsl"
       )
   elif has_legacy_opengl():
       shader = ShaderProgram(
           vertex_source_file="legacy_vertex.glsl",
           fragment_source_file="legacy_fragment.glsl"
       )
   else:
       # Use fallback shader
       shader = ShaderProgram(
           vertex_source=fallback_vertex_source,
           fragment_source=fallback_fragment_source
       )
