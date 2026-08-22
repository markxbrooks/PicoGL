"""Last-cursor state for GLUT drag rotation."""

from dataclasses import dataclass


@dataclass
class MouseInteraction:
    """Mouse Interaction"""

    last_x: int = 0
    last_y: int = 0
    dragging: bool = False

    def press(self, x: int, y: int) -> None:
        self.last_x = x
        self.last_y = y
        self.dragging = True

    def release(self) -> None:
        self.dragging = False

    def drag(self, x: int, y: int) -> tuple[int, int] | None:
        """Return (dx, dy) while dragging and update last position."""
        if not self.dragging:
            return None
        dx = x - self.last_x
        dy = y - self.last_y
        self.last_x = x
        self.last_y = y
        return dx, dy


@dataclass
class RotationInteraction(MouseInteraction):
    """Rotation Interaction"""

    x: float = 0.0
    y: float = 0.0

    def drag(self, x: int, y: int) -> tuple[float, float] | None:
        """Apply drag delta to rotation and return (rotation_x, rotation_y)."""
        delta = super().drag(x, y)
        if delta is None:
            return None
        dx, dy = delta
        self.x += dy * 0.5
        self.y += dx * 0.5
        return self.x, self.y

    def reset(self) -> None:
        self.x = 0.0
        self.y = 0.0

    def clamp_x(self, minimum: float = -90.0, maximum: float = 90.0) -> None:
        self.x = max(minimum, min(maximum, self.x))
