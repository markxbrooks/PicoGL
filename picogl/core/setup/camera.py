from molib.pdb.coordinate.coordinate import Coordinate3D
from picogl.backend.glu.lookat import glu_look_at_coords


def gl_setup_camera(zoom_distance: float):
    # Set up camera
    eye = Coordinate3D(0, 0, zoom_distance)
    center = Coordinate3D(0, 0, 0)
    up = Coordinate3D(0, 1, 0)
    # glu_look_at(0, 0, self.zoom_distance, 0, 0, 0, 0, 1, 0)
    glu_look_at_coords(eye=eye, center=center, up=up)
