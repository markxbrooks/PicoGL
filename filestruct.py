PicoGL file tree structure 

rom molib.pdb.coordinate.data import CoordinateData
from picogl.backend.legacy.core.camera.setup import calculate_aspect
from picogl.backend.modern.core.mvp import compute_mvp_zoom_from_zoom
from picogl.backend.modern.core.unproject import unproject
from picogl.backend.state import GLClipPlaneState, RenderState
from picogl.error import gl_check_errors
from picogl.mode import GLMode
from picogl.shaders.manager import ShaderManager
from picogl.shaders.type import ShaderType
from picogl.state.draw_mode import GLBitMask
from picogl.utils.gl_init import execute_gl_tasks, modern_init_gl_list
from pyglm import glm

from picogl.backend.capability import GLPipelineCapability
from picogl.backend.legacy.core.camera.lighting import (
    set_fog_state,
    set_second_light_state,
    setup_lighting,
    setup_lighting_mode_zero,
)
from picogl.backend.legacy.core.camera.matrix import update_camera_matrix
from picogl.backend.legacy.core.camera.setup import (
    calculate_aspect,
    enable_blending,
    enable_smoothing,
    setup_materials,
)
from picogl.backend.legacy.core.camera.unproject import unproject
from picogl.error import gl_check_errors
from picogl.frame import prepare_viewport
from picogl.mode import GLMode
from picogl.state.draw_mode import GLBitMask, GLLegacyClipPlane
from picogl.state.param import GLParam
from picogl.state.query import GLStateQuery
from picogl.utils.gl_init import GLTask, execute_gl_tasks

)
from molib.xtal.unit_cell import extract_unit_cell_from_pdb, validate_unit_cell
from picogl.backend.modern.core.mvp import compute_mvp_zoom_from_zoom
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.mode import GLMode
from picogl.renderer import MeshData
from picogl.state.param import GLParam
from picogl.state.query import GLStateQuery
from picogl.ui.backend.qt.base

rom molib.xtal.unit_cell import extract_unit_cell_from_pdb, validate_unit_cell
from picogl.backend.modern.core.mvp import compute_mvp_zoom_from_zoom
from picogl.buffers.vertex.vbo.vbo_class import VBOType
from picogl.mode import GLMode
from picogl.renderer import MeshData
from picogl.state.param import GLParam
from picogl.state.query import GLStateQuery
from picogl.backend.gl.driver.blend import GLBlendDriver
from picogl.backend.gl.driver.capability import GLCapabilityDriver
from picogl.backend.gl.driver.depth import GLDepthDriver
from picogl.backend.gl.driver.frame import GLFrameDriver
from picogl.backend.gl.driver.geometry import GLGeometryDriver
from picogl.backend.gl.driver.raster import GLRasterDriver
from picogl.backend.gl.driver.texture import GLTextureSystem
from picogl.backend.legacy.core.attribute_binder import LegacyAttributeBinder
from picogl.backend.legacy.core.pipeline import GLLegacyPipeline, LegacyPipeline
from picogl.backend.modern.core.pipeline import ShaderPipeline
from picogl.backend.opengl import GLBindingStrategy
from picogl.backend.state import (
    DrawCommand,
    GLClipPlaneState,
    GLStateManager,
    RenderState,
    RenderStateApplier,
)
from picogl.buffers.glframe import GLFramebuffer
from picogl.renderer.readback import GLReadback

from OpenGL.GL import glUseProgram

from picogl.renderer.initializable import Bindable

if TYPE_CHECKING:
    from picogl.backend.modern.core.shader.program import ShaderProgram

from picogl.backend.modern.core.vertex.array.helpers import (
    enable_points_rendering_state,
)
from picogl.backend.modern.core.vertex.base import VertexBuffer
from picogl.backend.modern.core.vertex.buffer.element import ModernEBO
from picogl.backend.modern.core.vertex.buffer.object import ModernVBO
from picogl.buffers.attributes import LayoutDescriptor
from picogl.buffers.base import VertexBase
from picogl.buffers.glcleanup import gl_delete_buffers, gl_delete_vertex_arrays
from picogl.buffers.vertex.aliases import NAME_ALIASES
from picogl.safe import gl_gen_safe
from picogl.state.draw_mode import (
    GLBufferTarget,
    GLDataType,
    GLDrawMode,
    GLIndexType,
    GLUsageHint,
)
from picogl.wrappers.buffer import gl_bind_buffer
from picogl.wrappers.draw import gl_draw_arrays, gl_draw_elements
from picogl.wrappers.enable_vertex_array import gl_enable_vertex_array
from picogl.wrappers.vertex_array import gl_bind_vertex_array
from picogl.wrappers.vertex_attrib_pointer import gl_vertex_attrib_pointer