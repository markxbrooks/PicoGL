import math

from picogl.core.camera import CameraParameters, ProjectionConfig
from pyglm import glm


class MVPControl:
    """Encapsulates camera position, orientation, and MVP matrix handling."""

    def __init__(self, width: int = 800, height: int = 480):
        self.fov = None
        self.z_angle = None
        self.position = None
        self.x_angle = None
        self.y_angle = None
        self.screen_width = width
        self.screen_height = height
        self.reset()

    def reset(self) -> None:
        """Reset to default camera position and orientation."""
        self.position = glm.vec3(5, 5, 5)
        self.x_angle = math.radians(225)  # yaw
        self.y_angle = math.radians(-35)  # pitch
        self.z_angle = 0.0  # roll (unused)
        self.fov = 60.0
        self.compute_matrices()

    def move_forward(self, distance: float) -> None:
        self.position += self.direction * distance
        self.compute_matrices()

    def move_up(self, distance: float) -> None:
        self.position += self.up * distance
        self.compute_matrices()

    def move_right(self, distance: float) -> None:
        self.position += self.right * distance
        self.compute_matrices()

    def pitch(self, delta: float) -> None:
        """Rotate camera up/down (pitch)."""
        self.y_angle += delta
        self.compute_matrices()

    def look_upward(self, yaw):
        """look_upward"""
        self.y_angle += yaw
        self.compute_matrices()

    def yaw(self, delta: float) -> None:
        """Rotate camera left/right (yaw)."""
        self.x_angle += delta
        self.compute_matrices()

    def turn(self, delta: float):
        self.yaw(delta)

    def set_fov(self, fov_degrees: float) -> None:
        """Change field of view."""
        self.fov = fov_degrees
        self.compute_matrices()

    def compute_matrices(self) -> None:
        """Recompute direction, right, up, and view/projection matrices."""
        self.direction = glm.vec3(
            math.cos(self.y_angle) * math.sin(self.x_angle),
            math.sin(self.y_angle),
            math.cos(self.y_angle) * math.cos(self.x_angle),
        )
        self.right = glm.vec3(
            math.sin(self.x_angle - math.pi / 2.0),
            0.0,
            math.cos(self.x_angle - math.pi / 2.0),
        )
        self.up = glm.cross(self.right, self.direction)
        self.look_pos = self.position + self.direction

        self.projection_matrix = ProjectionConfig(
            fovy=self.fov,
            aspect=self.screen_width / float(max(self.screen_height, 1)),
            near=ProjectionConfig().near,
            far=ProjectionConfig().far,
        ).matrix()
        self.view_matrix = CameraParameters(
            eye=self.position, center=self.look_pos, up=self.up
        ).view_matrix()

    def resize(self, width: int, height: int) -> None:
        """Resize the viewport and update projection matrix."""
        self.screen_width = width
        self.screen_height = height
        self.compute_matrices()

    def calc_mvp(self, model_matrix: glm.mat4) -> glm.mat4:
        """Return full MVP matrix for a given model transform."""
        return self.projection_matrix * self.view_matrix * model_matrix


def dummy_update_handler(self):
    print("dummy update method")
