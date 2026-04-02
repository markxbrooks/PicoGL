import numpy as np
from numpy import ndarray

from decologr import Decologr as log
from elmo.ui.state.view import ViewState
from picogl.renderer import MeshData


def attach_rgba_colors_to_mesh(colors: ndarray, mesh_data: MeshData, view: ViewState):
    """Attach RGBA colors expected by legacy isosurface renderer"""
    try:
        opacity = 1.0 - float(view.connolly_surface_transparency)
        rgba = np.hstack(
            (
                colors.astype(np.float32),
                np.full((len(colors), 1), opacity, dtype=np.float32),
            )
        )
        mesh_data.colors = rgba
        log.info(
            f"🎨 Connolly colors attached: {rgba.shape}",
            scope="attach_rgba_colors_to_mesh",
        )
    except Exception as ex:
        log.error(
            f"Failed to attach Connolly RGBA colors: {ex}",
            scope="attach_rgba_colors_to_mesh",
        )
