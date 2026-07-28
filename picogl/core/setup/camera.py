from picogl.backend.glu.lookat import glu_look_at_coords
from molib.pdb.coordinate.coordinate import Coordinates


def gl_setup_camera(zoom_distance: float):
    # Set up camera
    eye = Coordinates(0, 0, zoom_distance)
    center = Coordinates(0, 0, 0)
    up = Coordinates(0, 1, 0)
    # glu_look_at(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)
    glu_look_at_coords(eye=eye, center=center, up=up)