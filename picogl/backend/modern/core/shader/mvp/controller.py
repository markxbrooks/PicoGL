"""
Handles user input to manipulate MVPControl.

This module provides the MVPController class for handling user input, such as
keyboard and mouse events, to control an MVP transformation in a 3D scene. The
class supports special keys, such as arrow keys and page up/down, as well as
common keyboard inputs (like WASD) for navigation and movement. It also allows
for mouse-based interactions, including rotation and panning, to control the
scene's model-view-projection state.

Classes:
- MVPController: Inherits from MVPControl and implements input-related logic.
"""

from picogl.backend.modern.core.shader.mvp.control import MVPControl, dummy_update_handler
from picogl.backend.modern.core.shader.mvp.mouse import MouseMode


class MVPController(MVPControl):
    """Handles user input to manipulate MVPControl."""

    def __init__(self, update_callback=dummy_update_handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_callback = update_callback
        self.mouse_mode = MouseMode.NONE
        self.lastX = 0
        self.lastY = 0

    def on_special_key(self, key: int, x: int, y: int) -> None:
        """Handle special keys (arrows, page up/down, etc.)."""
        updated = False
        if key == 104:  # page down
            self.move_up(1.0)
            updated = True
        elif key == 105:  # page up
            self.move_up(-1.0)
            updated = True
        elif key == 101:  # up arrow
            self.look_upward(0.1)
            updated = True
        elif key == 103:  # down arrow
            self.look_upward(-0.1)
            updated = True
        elif key == 102:  # right arrow
            self.turn(0.1)
            updated = True
        elif key == 100:  # left arrow
            self.turn(-0.1)
            updated = True

        if updated:
            self.update_callback()

    def on_keyboard(self, key: str, x: int, y: int) -> None:
        """Handle keyboard keys (WASD)."""
        key = key.lower()
        updated = False
        if key == "w":
            self.move_forward(0.5)
            updated = True
        elif key == "s":
            self.move_forward(-0.5)
            updated = True
        elif key == "a":
            self.move_right(-0.5)
            updated = True
        elif key == "d":
            self.move_right(0.5)
            updated = True

        if updated:
            self.update_callback()

    def on_mouse(self, key: int, up: int, x: int, y: int) -> None:
        """Handle mouse button presses."""
        if key == 0 and up == 0:
            self.mouse_mode = MouseMode.ROTATE
            self.lastX, self.lastY = x, y
        elif key == 2 and up == 0:
            self.mouse_mode = MouseMode.PAN
            self.lastX, self.lastY = x, y
        else:
            self.mouse_mode = MouseMode.NONE
            self.lastX, self.lastY = -1, -1

    def on_mousemove(self, x: int, y: int) -> None:
        """Handle mouse movement."""
        delta_x = self.lastX - x
        delta_y = self.lastY - y

        if self.mouse_mode == MouseMode.ROTATE:
            self.lastX, self.lastY = x, y
            self.look_upward(delta_y * 0.01)
            self.turn(delta_x * 0.01)
            self.update_callback()
        elif self.mouse_mode == MouseMode.PAN:
            self.lastX, self.lastY = x, y
            self.move_up(-0.5 * delta_x)
            self.update_callback()
