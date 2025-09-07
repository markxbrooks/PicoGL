UI API
======

The UI module provides user interface functionality for PicoGL, including window management, input handling, and platform-specific backends.

Core Classes
------------

AbstractGLWindow
~~~~~~~~~~~~~~~~

.. autoclass:: picogl.ui.abc_window.AbstractGLWindow
   :members:
   :undoc-members:
   :show-inheritance:

The ``AbstractGLWindow`` class defines the interface for all PicoGL window implementations.

**Example**:

.. code-block:: python

   from picogl.ui.abc_window import AbstractGLWindow
   
   class MyWindow(AbstractGLWindow):
       def __init__(self):
           super().__init__()
           self.width = 800
           self.height = 600
       
       def initializeGL(self):
           # Initialize OpenGL
           pass
       
       def paintGL(self):
           # Render scene
           pass
       
       def resizeGL(self, width, height):
           # Handle resize
           pass

Window Backends
---------------

GLUT Backend
~~~~~~~~~~~~

GLWindow
^^^^^^^^

.. autoclass:: picogl.ui.backend.glut.window.gl.GLWindow
   :members:
   :undoc-members:
   :show-inheritance:

The ``GLWindow`` class provides a basic GLUT-based window implementation.

**Example**:

.. code-block:: python

   from picogl.ui.backend.glut.window.gl import GLWindow
   
   # Create GLUT window
   window = GLWindow(title="My Window")
   window.initializeGL()
   window.run()

GlutRendererWindow
^^^^^^^^^^^^^^^^^^

.. autoclass:: picogl.ui.backend.glut.window.glut.GlutRendererWindow
   :members:
   :undoc-members:
   :show-inheritance:

The ``GlutRendererWindow`` class provides a GLUT window with integrated rendering capabilities.

**Example**:

.. code-block:: python

   from picogl.ui.backend.glut.window.glut import GlutRendererWindow
   from picogl.renderer import GLContext, MeshData
   
   # Create renderer window
   context = GLContext()
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   window = GlutRendererWindow(
       width=800,
       height=600,
       title="Renderer Window",
       context=context,
       data=data
   )
   
   window.initializeGL()
   window.run()

RenderWindow
^^^^^^^^^^^^

.. autoclass:: picogl.ui.backend.glut.window.object.RenderWindow
   :members:
   :undoc-members:
   :show-inheritance:

The ``RenderWindow`` class provides a unified render window supporting both textured and untextured rendering.

**Example**:

.. code-block:: python

   from picogl.ui.backend.glut.window.object import RenderWindow
   from picogl.renderer import MeshData
   
   # Create render window
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   window = RenderWindow(
       width=800,
       height=600,
       title="Render Window",
       data=data,
       use_texture=False
   )
   
   window.initialize()
   window.run()

TextureWindow
^^^^^^^^^^^^^

.. autoclass:: picogl.ui.backend.glut.window.texture.TextureWindow
   :members:
   :undoc-members:
   :show-inheritance:

The ``TextureWindow`` class provides a window specialized for texture rendering.

**Example**:

.. code-block:: python

   from picogl.ui.backend.glut.window.texture import TextureWindow
   from picogl.renderer import MeshData
   
   # Create texture window
   data = MeshData.from_raw(vertices=vertices, uvs=uvs)
   
   window = TextureWindow(
       width=800,
       height=600,
       title="Texture Window",
       data=data,
       base_dir="resources/",
       use_texture=True
   )
   
   window.initialize()
   window.run()

Qt Backend
~~~~~~~~~~

GLBase
^^^^^^

.. autoclass:: picogl.ui.backend.qt.base.GLBase
   :members:
   :undoc-members:
   :show-inheritance:

The ``GLBase`` class provides a Qt-based OpenGL widget implementation.

**Example**:

.. code-block:: python

   from picogl.ui.backend.qt.base import GLBase
   from PyQt5.QtWidgets import QApplication, QMainWindow
   
   class MyGLWidget(GLBase):
       def __init__(self):
           super().__init__()
       
       def initializeGL(self):
           # Initialize OpenGL
           pass
       
       def paintGL(self):
           # Render scene
           pass
   
   # Create Qt application
   app = QApplication([])
   window = QMainWindow()
   widget = MyGLWidget()
   window.setCentralWidget(widget)
   window.show()
   app.exec_()

Input Handling
--------------

Mouse Input
~~~~~~~~~~~

**Mouse Press Events**:

.. code-block:: python

   def mousePressEvent(self, button, state, x, y):
       if button == GLUT_LEFT_BUTTON:
           if state == GLUT_DOWN:
               self.last_mouse_x = x
               self.last_mouse_y = y
           else:
               self.last_mouse_x = None
               self.last_mouse_y = None

**Mouse Motion Events**:

.. code-block:: python

   def motion(self, x, y):
       if self.last_mouse_x is not None and self.last_mouse_y is not None:
           dx = x - self.last_mouse_x
           dy = y - self.last_mouse_y
           
           self.rotation_y += dx * 0.5
           self.rotation_x += dy * 0.5
           
           self.last_mouse_x = x
           self.last_mouse_y = y
           glutPostRedisplay()

**Mouse Wheel Events**:

.. code-block:: python

   def mouse(self, button, state, x, y):
       if button == 3:  # Mouse wheel up
           self.zoom_distance = max(1.0, self.zoom_distance - 0.5)
       elif button == 4:  # Mouse wheel down
           self.zoom_distance = min(20.0, self.zoom_distance + 0.5)
       glutPostRedisplay()

Keyboard Input
~~~~~~~~~~~~~~

**Keyboard Events**:

.. code-block:: python

   def keyboard(self, key, x, y):
       if key == b'\x1b':  # ESC key
           sys.exit(0)
       elif key == b'r':  # Reset rotation
           self.rotation_x = 0.0
           self.rotation_y = 0.0
       elif key == b'w':  # Toggle wireframe
           self.wireframe_mode = not self.wireframe_mode
       glutPostRedisplay()

**Special Keys**:

.. code-block:: python

   def on_special_key(self, key, x, y):
       if key == GLUT_KEY_UP:
           self.rotation_x += 5.0
       elif key == GLUT_KEY_DOWN:
           self.rotation_x -= 5.0
       elif key == GLUT_KEY_LEFT:
           self.rotation_y += 5.0
       elif key == GLUT_KEY_RIGHT:
           self.rotation_y -= 5.0
       glutPostRedisplay()

Window Management
-----------------

Creating Windows
~~~~~~~~~~~~~~~~

**Basic Window**:

.. code-block:: python

   from picogl.ui.backend.glut.window.gl import GLWindow
   
   # Create basic window
   window = GLWindow(title="My Window")
   window.initializeGL()
   window.run()

**Renderer Window**:

.. code-block:: python

   from picogl.ui.backend.glut.window.object import RenderWindow
   from picogl.renderer import MeshData
   
   # Create renderer window
   data = MeshData.from_raw(vertices=vertices, colors=colors)
   
   window = RenderWindow(
       width=800,
       height=600,
       title="Renderer Window",
       data=data
   )
   
   window.initialize()
   window.run()

Window Properties
~~~~~~~~~~~~~~~~~

**Size and Position**:

.. code-block:: python

   # Set window size
   window.width = 800
   window.height = 600
   
   # Set window position
   window.x = 100
   window.y = 100

**Title and Icon**:

.. code-block:: python

   # Set window title
   window.title = "My PicoGL Application"
   
   # Set window icon (if supported)
   window.icon = "icon.png"

**Fullscreen Mode**:

.. code-block:: python

   # Toggle fullscreen
   window.toggle_fullscreen()
   
   # Check fullscreen state
   if window.is_fullscreen():
       print("Window is in fullscreen mode")

Rendering Loop
--------------

Display Function
~~~~~~~~~~~~~~~~

**Basic Display**:

.. code-block:: python

   def display(self):
       glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
       glLoadIdentity()
       
       # Set up camera
       gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
       
       # Apply transformations
       glRotatef(self.rotation_x, 1, 0, 0)
       glRotatef(self.rotation_y, 0, 1, 0)
       
       # Draw scene
       self.draw_scene()
       
       glutSwapBuffers()

**Advanced Display**:

.. code-block:: python

   def display(self):
       # Clear buffers
       glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
       glLoadIdentity()
       
       # Set up camera
       self.setup_camera()
       
       # Apply transformations
       self.apply_transformations()
       
       # Draw scene
       self.draw_scene()
       
       # Draw UI elements
       self.draw_ui()
       
       # Swap buffers
       glutSwapBuffers()

Resize Handling
~~~~~~~~~~~~~~~

**Basic Resize**:

.. code-block:: python

   def resizeGL(self, width, height):
       self.width = width
       self.height = height
       glViewport(0, 0, width, height)
       glMatrixMode(GL_PROJECTION)
       glLoadIdentity()
       gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
       glMatrixMode(GL_MODELVIEW)

**Advanced Resize**:

.. code-block:: python

   def resizeGL(self, width, height):
       self.width = width
       self.height = height
       
       # Update viewport
       glViewport(0, 0, width, height)
       
       # Update projection matrix
       self.update_projection_matrix(width, height)
       
       # Update UI layout
       self.update_ui_layout(width, height)
       
       # Notify renderers
       for renderer in self.renderers:
           renderer.resize(width, height)

Event Handling
--------------

Event Loop
~~~~~~~~~~

**Basic Event Loop**:

.. code-block:: python

   def run(self):
       glutMainLoop()

**Custom Event Loop**:

.. code-block:: python

   def run(self):
       while not self.should_exit:
           self.handle_events()
           self.update()
           self.render()
           self.sleep(16)  # 60 FPS

**Idle Function**:

.. code-block:: python

   def idle(self):
       if self.auto_rotate:
           self.rotation_y += 0.5
           glutPostRedisplay()

Timer Events
~~~~~~~~~~~~

**Basic Timer**:

.. code-block:: python

   def timer(self, value):
       # Update animation
       self.update_animation()
       
       # Redraw
       glutPostRedisplay()
       
       # Set next timer
       glutTimerFunc(16, self.timer, 0)  # 60 FPS

**Advanced Timer**:

.. code-block:: python

   def timer(self, value):
       # Update physics
       self.update_physics()
       
       # Update animation
       self.update_animation()
       
       # Update UI
       self.update_ui()
       
       # Redraw
       glutPostRedisplay()
       
       # Set next timer
       glutTimerFunc(16, self.timer, 0)

Platform-Specific Features
---------------------------

macOS
~~~~~

**Display Environment**:

.. code-block:: python

   import os
   
   # Check for display
   if os.environ.get('DISPLAY') is None:
       print("No display available")
       return
   
   # Run from Terminal.app or iTerm2
   window.run()

**OpenGL Context**:

.. code-block:: python

   # Check OpenGL version
   import OpenGL.GL as GL
   version = GL.glGetString(GL.GL_VERSION)
   print(f"OpenGL version: {version}")

Windows
~~~~~~~

**Graphics Drivers**:

.. code-block:: python

   # Check graphics vendor
   import OpenGL.GL as GL
   vendor = GL.glGetString(GL.GL_VENDOR)
   print(f"Graphics vendor: {vendor}")

**DLL Loading**:

.. code-block:: python

   # Check for required DLLs
   try:
       import OpenGL.GL as GL
   except ImportError as e:
       print(f"DLL loading failed: {e}")
       print("Install Visual C++ Redistributable")

Linux
~~~~~

**Display Server**:

.. code-block:: python

   import os
   
   # Check display
   display = os.environ.get('DISPLAY')
   if display:
       print(f"Using display: {display}")
   else:
       print("No display available")

**OpenGL Libraries**:

.. code-block:: python

   # Check OpenGL libraries
   try:
       import OpenGL.GL as GL
   except ImportError as e:
       print(f"OpenGL libraries not found: {e}")
       print("Install mesa libraries")

Error Handling
--------------

Window Creation Errors
~~~~~~~~~~~~~~~~~~~~~~

**Display Errors**:

.. code-block:: python

   try:
       window = GLWindow(title="My Window")
   except DisplayError as e:
       print(f"Display error: {e}")
       # Handle gracefully
   except Exception as e:
       print(f"Unexpected error: {e}")
       # Handle gracefully

**OpenGL Context Errors**:

.. code-block:: python

   try:
       window.initializeGL()
   except OpenGLError as e:
       print(f"OpenGL error: {e}")
       # Use fallback rendering
   except Exception as e:
       print(f"Unexpected error: {e}")
       # Handle gracefully

Input Errors
~~~~~~~~~~~~

**Mouse Input Errors**:

.. code-block:: python

   def mousePressEvent(self, button, state, x, y):
       try:
           # Handle mouse input
           pass
       except Exception as e:
           print(f"Mouse input error: {e}")
           # Handle gracefully

**Keyboard Input Errors**:

.. code-block:: python

   def keyboard(self, key, x, y):
       try:
           # Handle keyboard input
           pass
       except Exception as e:
           print(f"Keyboard input error: {e}")
           # Handle gracefully

Performance Considerations
-------------------------

**Frame Rate**:

.. code-block:: python

   # Target 60 FPS
   glutTimerFunc(16, self.timer, 0)  # 16ms = 60 FPS
   
   # Target 30 FPS
   glutTimerFunc(33, self.timer, 0)  # 33ms = 30 FPS

**Double Buffering**:

.. code-block:: python

   # Enable double buffering
   glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
   
   # Swap buffers
   glutSwapBuffers()

**VSync**:

.. code-block:: python

   # Enable VSync (if supported)
   import OpenGL.GL as GL
   GL.glEnable(GL.GL_VSYNC)

Best Practices
--------------

1. **Use appropriate window type** for your needs
2. **Handle input events** gracefully
3. **Implement proper resize handling**
4. **Use double buffering** for smooth rendering
5. **Test on multiple platforms** for compatibility

**Example**:

.. code-block:: python

   # Choose window type based on needs
   if needs_texture_rendering:
       window = TextureWindow(data=data, use_texture=True)
   elif needs_basic_rendering:
       window = RenderWindow(data=data)
   else:
       window = GLWindow(title="Basic Window")
   
   # Handle errors gracefully
   try:
       window.initialize()
       window.run()
   except Exception as e:
       print(f"Window error: {e}")
       # Handle gracefully
