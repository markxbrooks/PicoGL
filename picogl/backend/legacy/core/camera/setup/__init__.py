from picogl.backend.legacy.core.camera.setup.aspect import calculate_aspect_ratio
from picogl.backend.legacy.core.camera.setup.blend import enable_blending
from picogl.backend.legacy.core.camera.setup.depth import enable_depth_test
from picogl.backend.legacy.core.camera.setup.materials import setup_materials
from picogl.backend.legacy.core.camera.setup.smooth import enable_smoothing

# Backward-compatible alias (deprecated)
calculate_aspect = calculate_aspect_ratio
