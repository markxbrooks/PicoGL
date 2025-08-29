"""
Axes visualization for crystallographic structures.

This module provides functionality to render coordinate axes
as colored lines with labels.
"""

import numpy as np
from OpenGL import GL
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12

from elmo.gl.buffers.factory.abstract import create_layout, create_common_attributes
from picogl.backend.legacy.gizmos.axes.array import AxesVBG

from picogl.logger import Logger as log

# Initialize GLUT once when the module is imported
try:
    glutInit()
    log.info("✅ GLUT initialized successfully for text rendering")
except Exception as e:
    log.warning(f"⚠️ GLUT initialization failed: {e}. Text labels will be disabled.")
    GLUT_AVAILABLE = False
else:
    GLUT_AVAILABLE = True


class AxesRenderer:
    """
    Renders coordinate axes as colored lines with labels.

    The axes are rendered as three colored lines (X=red, Y=green, Z=blue)
    with text labels that can be toggled on/off.
    """

    def __init__(self):
        """Initialize the axes renderer."""
        self.vbg = None
        self.unit_cell_info = None
        self.vertices = None
        self.colors = None
        self.is_initialized = False
        self.visible = True
        self.show_labels = True  # Whether to show axis labels
        self.line_width = 2.0
        self.axis_length = 50.0  # Length of axes in Angstroms
        self.label_offset = 5.0  # Offset for labels from axis endpoints

    def set_unit_cell(self, unit_cell_info: dict) -> None:
        """
        Set the unit cell parameters and generate the geometry.

        Args:
            unit_cell_info: Dictionary containing unit cell parameters:
                - 'a', 'b', 'c': Unit cell lengths in Angstroms
                - 'alpha', 'beta', 'gamma': Unit cell angles in degrees
                - 'space_group': Space group information (optional)
        """
        if not unit_cell_info:
            log.warning("No unit cell information provided")
            return

        self.unit_cell_info = unit_cell_info
        self._generate_geometry()
        self.initialize_buffers()
        # Note: is_initialized is now set in initialize_buffers() after successful initialization
        log.info(
            f"✅ Axes set for unit cell: a={unit_cell_info['a']:.2f}, "
            f"b={unit_cell_info['b']:.2f}, c={unit_cell_info['c']:.2f} Å"
        )

    def _generate_geometry(self) -> None:
        """Generate the axes vertices and colors."""
        # Create three axes: X (red), Y (green), Z (blue)
        # Each axis is a line from origin to axis_length
        self.vertices = np.array([
            # X-axis (red)
            0.0, 0.0, 0.0,      # Origin
            self.axis_length, 0.0, 0.0,  # X endpoint
            
            # Y-axis (green)  
            0.0, 0.0, 0.0,      # Origin
            0.0, self.axis_length, 0.0,  # Y endpoint
            
            # Z-axis (blue)
            0.0, 0.0, 0.0,      # Origin
            0.0, 0.0, self.axis_length,  # Z endpoint
        ], dtype=np.float32)
        
        self.colors = np.array([
            # X-axis (red)
            1.0, 0.0, 0.0,      # Origin
            1.0, 0.0, 0.0,      # X endpoint
            
            # Y-axis (green)
            0.0, 1.0, 0.0,      # Origin
            0.0, 1.0, 0.0,      # Y endpoint
            
            # Z-axis (blue)
            0.0, 0.0, 1.0,      # Origin
            0.0, 0.0, 1.0,      # Z endpoint
        ], dtype=np.float32)

    def initialize_buffers(self) -> None:
        """Initialize the vertex buffer objects for rendering."""
        if self.is_initialized:
            log.message("Axes buffers already initialized")
            return
            
        # Check if we have a valid OpenGL context
        try:
            GL.glGetError()  # Clear any previous errors
        except Exception as e:
            log.error(f"OpenGL context not available during buffer initialization: {e}")
            self.is_initialized = False
            return
            
        try:
            self.vbg = AxesVBG()
            
            # Validate that we have data to work with
            if self.vertices is None or self.colors is None:
                log.error("No vertex or color data available for buffer initialization")
                self.is_initialized = False
                return
            axes_layout = create_layout(create_common_attributes())
            # Add position VBO (vertices)
            self.vbg.add_vbo(name="vbo", data=self.vertices, size=3)
            # Add color VBO (colors)
            self.vbg.add_vbo(name="cbo", data=self.colors, size=3)
            self.vbg.set_layout(axes_layout)
            # Verify that VBOs were created successfully
            if not hasattr(self.vbg, 'named_vbos') or len(self.vbg.named_vbos) < 2:
                log.error("Failed to create required VBOs")
                self.is_initialized = False
                return
                
            self.is_initialized = True
            log.info("✅ Axes buffers initialized successfully")
            
        except Exception as e:
            log.error(f"Error initializing axes buffers: {e}")
            self.is_initialized = False

    def render(self) -> None:
        """Draw the axes using vertex buffer objects."""
        # Use the safe render method
        self._render_array_safe()
        
    def _render_array_safe(self) -> None:
        """Safe implementation of render_array with comprehensive error checking."""
        if not self.is_initialized or not self.visible:
            log.debug(f"Axes not ready: is_initialized={self.is_initialized}, visible={self.visible}")
            return
            
        if self.vbg is None:
            log.error("Axes VBG is None - cannot render")
            return
            
        # Check if we can render safely
        if not self.can_render_safely():
            log.warning("Cannot render safely - falling back to immediate mode")
            self._render_immediate_fallback()
            return
            
        # Validate OpenGL context
        try:
            # Check if we have a valid OpenGL context
            GL.glGetError()  # Clear any previous errors
        except Exception as e:
            log.error(f"OpenGL context not available: {e}")
            # Fallback to immediate mode
            self._render_immediate_fallback()
            return
            
        # Save current OpenGL state - only push necessary attributes
        try:
            GL.glPushAttrib(GL.GL_LINE_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
        except Exception as e:
            log.error(f"Failed to save OpenGL state: {e}")
            # Fallback to immediate mode
            self._render_immediate_fallback()
            return
        
        # Set line properties
        try:
            GL.glLineWidth(self.line_width)
            GL.glDisable(GL.GL_DEPTH_TEST)  # Draw on top
            GL.glEnable(GL.GL_LINE_SMOOTH)
        except Exception as e:
            log.error(f"Failed to set OpenGL line properties: {e}")
            # Continue anyway, these are not critical
            
        try:
            # Draw the axes using vertex buffers
            self.vbg.draw()
            log.debug("Axes rendered successfully using VBOs", silent=True)
            
        except Exception as e:
            log.error(f"Error rendering axes with VBOs: {e}")
            # Fallback to immediate mode rendering if VBO fails
            log.info("Falling back to immediate mode rendering")
            self._render_immediate_fallback()
            
        finally:
            # Render labels if enabled
            if self.show_labels:
                try:
                    self._render_labels()
                except Exception as e:
                    log.error(f"Error rendering labels: {e}")
                    
            # Restore OpenGL state
            try:
                GL.glPopAttrib()
            except Exception as e:
                log.error(f"Error restoring OpenGL state: {e}")
                
    def _render_immediate_fallback(self) -> None:
        """Fallback rendering method using immediate mode when VBOs fail."""
        try:
            # Use immediate mode rendering for simplicity
            GL.glBegin(GL.GL_LINES)
            
            # X-axis (red)
            GL.glColor3f(1.0, 0.0, 0.0)
            GL.glVertex3f(0.0, 0.0, 0.0)
            GL.glVertex3f(self.axis_length, 0.0, 0.0)
            
            # Y-axis (green)
            GL.glColor3f(0.0, 1.0, 0.0)
            GL.glVertex3f(0.0, 0.0, 0.0)
            GL.glVertex3f(0.0, self.axis_length, 0.0)
            
            # Z-axis (blue)
            GL.glColor3f(0.0, 0.0, 1.0)
            GL.glVertex3f(0.0, 0.0, 0.0)
            GL.glVertex3f(0.0, 0.0, self.axis_length)
            
            GL.glEnd()
            log.debug("Axes rendered successfully using immediate mode fallback")
            
        except Exception as e:
            log.error(f"Error in immediate mode fallback: {e}")

    def render_instanced(self) -> None:
        """Render the coordinate axes using OpenGL 2.1 compatible code."""
        if not self.is_initialized or not self.visible:
            return

        # Save current OpenGL state - only push necessary attributes
        GL.glPushAttrib(GL.GL_LINE_BIT | GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)

        # Set line properties
        GL.glLineWidth(self.line_width)
        GL.glDisable(GL.GL_DEPTH_TEST)  # Draw on top
        GL.glEnable(GL.GL_LINE_SMOOTH)

        # Use immediate mode rendering for simplicity
        GL.glBegin(GL.GL_LINES)
        
        # X-axis (red)
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(self.axis_length, 0.0, 0.0)
        
        # Y-axis (green)
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(0.0, self.axis_length, 0.0)
        
        # Z-axis (blue)
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0.0, 0.0, 0.0)
        GL.glVertex3f(0.0, 0.0, self.axis_length)
        
        GL.glEnd()

        # Render labels if enabled
        if self.show_labels:
            self._render_labels()

        # Restore OpenGL state
        GL.glPopAttrib()

    def _render_labels(self) -> None:
        """Render text labels for the axes."""
        if not GLUT_AVAILABLE:
            # Fallback to visual indicators if GLUT is not available
            self._render_fallback_indicators()
            return
            
        # Set text color to white for better visibility
        GL.glColor3f(1.0, 1.0, 1.0)
        
        # X-axis label
        self._render_text_label("X", self.axis_length + self.label_offset, 0.0, 0.0)
        
        # Y-axis label  
        self._render_text_label("Y", 0.0, self.axis_length + self.label_offset, 0.0)
        
        # Z-axis label
        self._render_text_label("Z", 0.0, 0.0, self.axis_length + self.label_offset)

    def _render_text_label(self, text: str, x: float, y: float, z: float) -> None:
        """
        Render a text label at the specified 3D position.
        
        Args:
            text: Text to render
            x, y, z: 3D coordinates for the label
        """
        # Set the raster position for text
        GL.glRasterPos3f(x, y, z)
        
        # Render the text character by character
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    def _render_fallback_indicators(self) -> None:
        """Render fallback visual indicators when GLUT is not available."""
        # X-axis indicator (red)
        GL.glColor3f(1.0, 0.0, 0.0)
        self._render_axis_indicator(self.axis_length + self.label_offset, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Y-axis indicator (green)
        GL.glColor3f(0.0, 1.0, 0.0)
        self._render_axis_indicator(0.0, self.axis_length + self.label_offset, 0.0, 0.0, 0.0, 0.0)
        
        # Z-axis indicator (blue)
        GL.glColor3f(0.0, 0.0, 1.0)
        self._render_axis_indicator(0.0, 0.0, self.axis_length + self.label_offset, 0.0, 0.0, 0.0)

    def _render_axis_indicator(self, x: float, y: float, z: float, dx: float, dy: float, dz: float) -> None:
        """
        Render a small visual indicator at the specified 3D position.
        
        Args:
            x, y, z: 3D coordinates for the indicator
            dx, dy, dz: Direction vector for the indicator
        """
        # Render a small cross or dot to indicate the axis endpoint
        # This is a simple visual indicator that doesn't require GLUT
        
        indicator_size = 2.0  # Size of the indicator in Angstroms
        
        # Draw a small cross at the axis endpoint
        GL.glBegin(GL.GL_LINES)
        
        # Horizontal line of the cross
        GL.glVertex3f(x - indicator_size, y, z)
        GL.glVertex3f(x + indicator_size, y, z)
        
        # Vertical line of the cross (if not Z-axis)
        if abs(dz) < 0.1:  # If this is X or Y axis
            GL.glVertex3f(x, y - indicator_size, z)
            GL.glVertex3f(x, y + indicator_size, z)
        else:  # If this is Z axis
            GL.glVertex3f(x, y, z - indicator_size)
            GL.glVertex3f(x, y, z + indicator_size)
        
        GL.glEnd()

    def set_visibility(self, visible: bool) -> None:
        """Set the visibility of the axes."""
        self.visible = visible
        log.info(f"Axes visibility: {'ON' if visible else 'OFF'}")

    def set_labels_visibility(self, visible: bool) -> None:
        """Set the visibility of the axis labels."""
        self.show_labels = visible
        log.info(f"Axis labels visibility: {'ON' if visible else 'OFF'}")

    def set_line_width(self, width: float) -> None:
        """Set the line width of the axes."""
        self.line_width = max(1.0, width)
        log.info(f"Axes line width set to {self.line_width}")

    def set_axis_length(self, length: float) -> None:
        """Set the length of the axes."""
        self.axis_length = max(1.0, length)
        if self.unit_cell_info:
            self._generate_geometry()
        log.info(f"Axes length set to {self.axis_length} Å")

    def set_label_offset(self, offset: float) -> None:
        """Set the offset for labels from axis endpoints."""
        self.label_offset = max(0.0, offset)
        log.info(f"Label offset set to {self.label_offset} Å")

    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        try:
            if self.vbg is not None:
                # Clean up VBOs if they exist
                if hasattr(self.vbg, 'named_vbos'):
                    for vbo in self.vbg.named_vbos.values():
                        try:
                            if hasattr(vbo, 'delete'):
                                vbo.delete()
                        except Exception as e:
                            log.error(f"Error deleting VBO: {e}")
                            
                # Clean up the VBG itself
                try:
                    if hasattr(self.vbg, 'delete'):
                        self.vbg.delete()
                except Exception as e:
                    log.error(f"Error deleting VBG: {e}")
                    
            self.vbg = None
            self.vertices = None
            self.colors = None
            self.is_initialized = False
            log.info("✅ Axes OpenGL resources cleaned up")
            
        except Exception as e:
            log.error(f"Error during cleanup: {e}")
            # Force cleanup even if there are errors
            self.vbg = None
            self.vertices = None
            self.colors = None
            self.is_initialized = False
        
    def is_ready(self) -> bool:
        """Check if the renderer is ready to render."""
        return (self.is_initialized and 
                self.visible and 
                self.vbg is not None and 
                self.vertices is not None and 
                self.colors is not None)
                
    def get_status(self) -> dict:
        """Get the current status of the renderer for debugging."""
        return {
            'is_initialized': self.is_initialized,
            'visible': self.visible,
            'show_labels': self.show_labels,
            'vbg_exists': self.vbg is not None,
            'vertices_exist': self.vertices is not None,
            'colors_exist': self.colors is not None,
            'axis_length': self.axis_length,
            'line_width': self.line_width,
            'unit_cell_info': self.unit_cell_info
        }
        
    def test_render(self) -> bool:
        """Test if the renderer can render by checking all components."""
        if not self.is_ready():
            log.error("Renderer not ready")
            return False
            
        if self.vbg is None:
            log.error("VBG is None")
            return False
            
        if not hasattr(self.vbg, 'named_vbos') or not self.vbg.named_vbos:
            log.error("VBG has no named VBOs")
            return False
            
        log.info(f"✅ Renderer test passed. VBOs: {list(self.vbg.named_vbos.keys())}")
        return True
        
    def can_render_safely(self) -> bool:
        """Check if the renderer can safely render in the current OpenGL context."""
        try:
            # Check if we have a valid OpenGL context
            GL.glGetError()
            
            # Check if we're in a valid rendering state
            if not self.is_ready():
                return False
                
            # Check if VBOs are properly set up
            if not self.vbg or not hasattr(self.vbg, 'named_vbos'):
                return False
                
            # Check if required VBOs exist and have data
            required_vbos = ['vbo', 'cbo']
            for name in required_vbos:
                if name not in self.vbg.named_vbos:
                    return False
                vbo = self.vbg.named_vbos[name]
                if not vbo or not hasattr(vbo, 'data') or vbo.data is None:
                    return False
                    
            return True
            
        except Exception as e:
            log.error(f"Error checking render safety: {e}")
            return False
            
    def reset(self) -> None:
        """Reset the renderer to a safe state."""
        try:
            log.info("Resetting axes renderer...")
            self.cleanup()
            
            # Reinitialize if we have unit cell info
            if self.unit_cell_info:
                self._generate_geometry()
                self.initialize_buffers()
                
            log.info("✅ Axes renderer reset completed")
            
        except Exception as e:
            log.error(f"Error resetting renderer: {e}")
            # Force a clean state
            self.is_initialized = False
            self.vbg = None
            self.vertices = None
            self.colors = None
