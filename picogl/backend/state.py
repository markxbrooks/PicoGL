"""
Render-state descriptors and command helpers for PicoGL backends.

The classes in this module are intentionally backend-neutral: they describe
desired OpenGL state and delegate the actual gl calls to a backend object.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
from picogl.backend.gl.enums.legacy.scale import gl_viewport
from picogl.backend.gl.state.client import GLClientState
from picogl.backend.gl.wrappers.blending import gl_blend_func
from numpy import ndarray
from picogl.backend.gl.capability import (
    GLBlendFactor,
    GLFixedFunctionCapability,
    GLPipelineCapability,
)
from picogl.backend.gl.enums import GLDrawMode, GLIndexType, GLNumeric
from picogl.backend.gl.enums.point_size import GLPointCapability
from picogl.backend.gl.state.fill import GLCapability, GLFace, GLFillMode
from picogl.backend.gl.wrappers import gl_draw_elements, gl_enable_legacy_client_state
from picogl.backend.gl.wrappers.pointer import (
    gl_color_array_pointer,
    gl_normal_array_pointer,
    gl_vertex_array_pointer,
)
from picogl.backend.value import gl_value
from picogl.texture.gltexture_driver import GLTextureDriver


class CapabilityDriver(Protocol):
    """Capability Driver"""

    def enable(self, cap: int) -> None: ...
    def disable(self, cap: int) -> None: ...


@dataclass(frozen=True)
class RasterState:
    """Raster State"""

    polygon_mode: Any = GLFillMode.FILL
    line_width: float = 1.0
    polygon_offset: tuple[float, float] = (0.0, 0.0)
    point_size: float | None = None

    def apply(self, backend: Any) -> None:
        """
        Applies rendering properties to the given backend.

        This method configures the rendering settings of the provided backend
        based on its attributes. It will utilize the appropriate backend's
        methods to apply the rendering properties.

        Parameters:
        backend (Any): The rendering backend to apply the settings to. The backend should
            have either a 'raster' attribute with an 'apply()' method or methods
            for setting polygon mode and line width.

        Returns:
        None
        """
        if hasattr(backend, "raster"):
            backend.raster.apply(self)
            return
        if hasattr(backend, "set_line_width"):
            backend.set_polygon_mode(GLFace.FRONT_AND_BACK, gl_value(self.polygon_mode))
            backend.set_line_width(self.line_width)


class GLStateManager:
    """Tracks capability state without querying OpenGL."""

    def __init__(self, backend: CapabilityDriver):
        self.backend = backend
        self._caps: dict[int, bool] = {}

    def set_enabled(self, cap: int, enabled: bool) -> None:
        """
        Sets the state of a specific capability.

        This method enables or disables a given capability based on the specified flag.
        It ensures that the backend is updated only if the capability's state changes.

        Parameters:
        cap: int
            The capability to be enabled or disabled.
        enabled: bool
            A boolean value indicating whether to enable (True) or disable (False) the capability.

        Returns:
        None
        """
        cap = gl_value(cap)
        enabled = bool(enabled)
        if self._caps.get(cap) == enabled:
            return
        self._caps[cap] = enabled

        if enabled:
            self.backend.enable(cap)
        else:
            self.backend.disable(cap)

    def is_enabled(self, cap: int) -> bool:
        """
        Determines if a specific capability is enabled.

        This method checks whether a given capability, identified by its
        integer representation, is currently enabled. The capability's
        value is processed using the `gl_value` function, and the result
        is determined by querying the internal data structure.

        Parameters:
        cap: int
            The integer representation of the capability to check.

        Returns:
        bool
            True if the specified capability is enabled, False otherwise.
        """
        return self._caps.get(gl_value(cap), False)


@dataclass(frozen=True)
class BlendState:
    """Blend State"""

    enabled: bool = False
    src: Any = GLBlendFactor.SRC_ALPHA
    dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA

    def apply(self, state: GLStateManager):
        """
        Applies blending state to the given GLStateManager.

        This method adjusts the blending settings in the given OpenGL state manager
        based on the current configuration. If the backend of the GLStateManager
        supports blending and has a custom implementation, that custom behavior is
        invoked; otherwise, standard OpenGL blending state is configured.

        Parameters:
        state (GLStateManager): The state manager to which the blending configuration
          should be applied.

        """
        backend = state.backend
        if hasattr(backend, "blend"):
            backend.blend.apply(self)
            return
        state.set_enabled(GLPipelineCapability.BLEND, self.enabled)
        if self.enabled:
            gl_blend_func(gl_value(self.src), gl_value(self.dst))


@dataclass(frozen=True, init=False)
class DepthState:
    """
    Represents depth-related state settings used for rendering.

    This class encapsulates settings for depth test and depth write functionalities,
    commonly used in rendering pipelines. It ensures immutability, allowing safe usage
    in contexts where concurrent access or state integrity is required. The class
    provides mechanisms to apply depth states to an OpenGL rendering backend.

    Attributes
    ----------
    test : bool
        Indicates whether depth testing is enabled (True) or disabled (False).
    write : bool
        Indicates whether depth writing is enabled (True) or disabled (False).
    """

    test: bool = True
    write: bool = True

    def __init__(
        self,
        test: bool = True,
        write: bool = True,
        enabled: bool | None = None,
    ):
        if enabled is not None:
            test = enabled
        object.__setattr__(self, "test", bool(test))
        object.__setattr__(self, "write", bool(write))

    @property
    def enabled(self) -> bool:
        """
        Checks if the feature is currently enabled.

        This property determines whether the feature or functionality controlled by
        the associated test attribute is active or not.

        Returns
        -------
        bool
            True if the feature is enabled, False otherwise.
        """
        return self.test

    def apply(self, state: GLStateManager):
        """
        Applies depth-related settings to the given GLStateManager.

        The method interacts with the provided GLStateManager to configure depth
        test and depth write capabilities. If the backend associated with the
        GLStateManager supports depth operations directly, it delegates the
        application of these settings to the backend; otherwise, it sets the
        appropriate GL pipeline capabilities and depth write settings.

        Parameters:
        state (GLStateManager): The state manager used to manage OpenGL states and
                                 capabilities.

        Raises:
        None
        """
        backend = state.backend
        if hasattr(backend, "depth"):
            backend.depth.apply(self)
            return
        state.set_enabled(GLPipelineCapability.DEPTH_TEST, self.test)
        state.backend.set_depth_write(self.write)


@dataclass(frozen=True, init=False)
class RenderState:
    """
    Represents the rendering state configuration for a graphics pipeline.

    The RenderState class encapsulates various rendering states such as blending, depth
    testing, polygon rendering modes, and other state-related settings. This class is
    intended to provide an immutable configuration object for managing rendering behavior.

    Attributes
    ----------
    blend : bool
        Whether blending is enabled.
    blend_src : Any
        The source blend factor for blending operations.
    blend_dst : Any
        The destination blend factor for blending operations.
    depth_test : bool
        Indicates whether depth testing is enabled.
    depth_write : bool
        Specifies if writing to the depth buffer is enabled.
    line_width : float
        The width of rendered lines.
    polygon_mode : Any
        The polygon rendering mode.
    polygon_offset : tuple[float, float]
        The polygon offset as a (factor, units) tuple.
    point_size : float | None
        The size of rendered points. None indicates default size.
    program_point_size : bool
        Indicates whether point size is controlled by the program.
    cull_face : bool
        Whether face culling is enabled.
    lighting : bool
        Whether lighting calculations are enabled.

    Methods
    -------
    raster
        Retrieve the rasterization state represented by a RasterState object.
    depth
        Retrieve the depth state represented by a DepthState object.
    blend_state
        Retrieve the blend state represented by a BlendState object.
    """

    blend: bool = False
    blend_src: Any = GLBlendFactor.SRC_ALPHA
    blend_dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA
    depth_test: bool = True
    depth_write: bool = True
    line_width: float = 1.0
    polygon_mode: Any = GLFillMode.FILL
    polygon_offset: tuple[float, float] = (0.0, 0.0)
    point_size: float | None = None
    program_point_size: bool = False
    cull_face: bool = False
    lighting: bool = False

    def __init__(
        self,
        *,
        raster: RasterState | None = None,
        depth: DepthState | None = None,
        blend: BlendState | bool | None = None,
        blend_src: Any = GLBlendFactor.SRC_ALPHA,
        blend_dst: Any = GLBlendFactor.ONE_MINUS_SRC_ALPHA,
        depth_test: bool | None = None,
        depth_write: bool | None = None,
        line_width: float | None = None,
        polygon_mode: Any | None = None,
        polygon_offset: tuple[float, float] | None = None,
        point_size: float | None = None,
        program_point_size: bool = False,
        cull_face: bool = False,
        lighting: bool = False,
    ):
        if raster is not None:
            line_width = raster.line_width if line_width is None else line_width
            polygon_mode = raster.polygon_mode if polygon_mode is None else polygon_mode
            polygon_offset = (
                raster.polygon_offset if polygon_offset is None else polygon_offset
            )
            point_size = raster.point_size if point_size is None else point_size

        if depth is not None:
            depth_test = depth.test if depth_test is None else depth_test
            depth_write = depth.write if depth_write is None else depth_write

        if isinstance(blend, BlendState):
            blend_src = blend.src
            blend_dst = blend.dst
            blend_enabled = blend.enabled
        else:
            blend_enabled = bool(blend) if blend is not None else False

        object.__setattr__(self, "blend", bool(blend_enabled))
        object.__setattr__(self, "blend_src", blend_src)
        object.__setattr__(self, "blend_dst", blend_dst)
        object.__setattr__(
            self,
            "depth_test",
            True if depth_test is None else bool(depth_test),
        )
        object.__setattr__(
            self,
            "depth_write",
            True if depth_write is None else bool(depth_write),
        )
        object.__setattr__(
            self,
            "line_width",
            1.0 if line_width is None else float(line_width),
        )
        object.__setattr__(
            self,
            "polygon_mode",
            GLFillMode.FILL if polygon_mode is None else polygon_mode,
        )
        object.__setattr__(
            self,
            "polygon_offset",
            (0.0, 0.0) if polygon_offset is None else tuple(polygon_offset),
        )
        object.__setattr__(self, "point_size", point_size)
        object.__setattr__(self, "program_point_size", bool(program_point_size))
        object.__setattr__(self, "cull_face", bool(cull_face))
        object.__setattr__(self, "lighting", bool(lighting))

    @property
    def raster(self) -> RasterState:
        """
        Property to retrieve the rasterization state.

        The raster property gathers various rendering state settings related
        to rasterization and combines them into a RasterState object.

        Returns:
            RasterState: An object representing the rasterization settings,
            including polygon mode, line width, polygon offset, and point size.
        """
        return RasterState(
            polygon_mode=self.polygon_mode,
            line_width=self.line_width,
            polygon_offset=self.polygon_offset,
            point_size=self.point_size,
        )

    @property
    def depth(self) -> DepthState:
        """
        Returns the DepthState object representing the current depth state.

        The DepthState object encapsulates whether depth testing is enabled,
        and whether depth writing is allowed. This property provides a way to
        retrieve the current state of depth testing and writing configured
        in the system.

        Returns
        -------
        DepthState
            An object combining depth test and depth write settings, where
            `test` reflects the current depth test state and `write`
            reflects the current depth write state.
        """
        return DepthState(test=self.depth_test, write=self.depth_write)

    @property
    def blend_state(self) -> BlendState:
        """
        Retrieve the blend state of the object.

        Provides the configuration of the blending state based on the object's
        current attributes.

        Returns:
            BlendState: An object representing the blend state, including whether
            blending is enabled and the source and destination blend factors.
        """
        return BlendState(
            enabled=self.blend,
            src=self.blend_src,
            dst=self.blend_dst,
        )


class RenderStateApplier:
    """
    Manages the application of render states to a backend.

    This class ensures that a given render state is applied incrementally
    to a backend, avoiding redundant operations. The purpose is to optimize
    rendering performance by minimizing redundant state changes. The `apply`
    method orchestrates the comparison of the current state with a new state
    and applies only the necessary differences.

    Attributes:
        backend (Any): The rendering backend to which the render states
            are applied.
        current (RenderState | None): The current render state that has
            been applied. This is updated each time a new state is applied.

    Methods:
        apply(state: RenderState):
            Applies a given render state to the backend. Only applies differences
            compared to the currently applied state to optimize the rendering
            process.
    """

    def __init__(self, backend: Any):
        self.backend = backend
        self.current: RenderState | None = None

    def apply(self, state: RenderState):
        if self.current == state:
            return

        prev = self.current
        self.current = state

        if prev is None or prev.raster != state.raster:
            self.backend.raster.apply(state.raster)

        if prev is None or prev.depth != state.depth:
            self.backend.depth.apply(state.depth)

        if prev is None or prev.blend_state != state.blend_state:
            self.backend.blend.apply(state.blend_state)

        if prev is None or prev.cull_face != state.cull_face:
            self.backend.capabilities.set_enabled(
                GLPipelineCapability.CULL_FACE,
                state.cull_face,
            )

        # Core-profile contexts reject GL_LIGHTING; modern draws use shader lighting.
        if state.lighting and (prev is None or not prev.lighting):
            self.backend.capabilities.set_enabled(
                GLFixedFunctionCapability.LIGHTING,
                True,
            )

        if state.program_point_size and (prev is None or not prev.program_point_size):

            self.backend.capabilities.enable(GLPointCapability.PROGRAM_POINT_SIZE)
        elif (
            prev is not None
            and prev.program_point_size
            and not state.program_point_size
        ):

            self.backend.capabilities.disable(GLPointCapability.PROGRAM_POINT_SIZE)


class GLVertexBuffer:
    def __init__(self, data: ndarray):
        self.data = data

    def bind_legacy(self):
        # fallback path
        pass


@dataclass
class GLAttributeArray:
    """gl Attribute Array"""

    size: int
    dtype: Any
    stride: int
    pointer: Any

    def enable_legacy(self, kind: GLClientState):
        """
        Enables the legacy client state for a specific OpenGL client state.

        This method enables the specified OpenGL client state by calling the
        appropriate `gl_enable_legacy_client_state` function and then uses a
        corresponding handler to configure the relevant pointer settings for
        the client state. If the given client state is unsupported by the
        handlers, a `RuntimeError` is raised.

        Parameters:
        kind (GLClientState): The type of OpenGL client state to enable. This
        determines the specific handler to be invoked for configuring pointer
        settings.

        Raises:
        RuntimeError: If the argument `kind` cannot be processed by any of the
        handlers provided in the method.
        """
        gl_enable_legacy_client_state(kind)
        handlers = {
            GLClientState.VERTEX: gl_vertex_array_pointer,
            GLClientState.NORMAL: gl_normal_array_pointer,
            GLClientState.COLOR_ARRAY: gl_color_array_pointer,
        }
        handler = handlers.get(kind, None)
        if handler is None:
            raise RuntimeError(f"kind {kind} not handled: {kind}")
        handler(
            pointer=self.pointer,
            size=self.size,
            num_type=GLNumeric.FLOAT,
            stride=self.stride,
        )


@dataclass
class GLViewport:
    """
    Represents a viewport in OpenGL with specified position and dimensions.

    This class encapsulates the functionality of an OpenGL viewport, allowing
    the user to define the x and y position, as well as the width and height
    of the viewport. The `apply` method sets the viewport in the OpenGL
    context using the specified attributes.

    Attributes:
        x: int
            The x-coordinate of the lower-left corner of the viewport.
        y: int
            The y-coordinate of the lower-left corner of the viewport.
        width: int
            The width of the viewport in pixels.
        height: int
            The height of the viewport in pixels.
    """

    x: int
    y: int
    width: int
    height: int

    def apply(self):
        """
        Adjusts the viewport to the specified dimensions and coordinates.

        The `apply` method sets the area of the window where OpenGL draws content. It
        defines the x and y coordinates of the lower-left corner of the viewport, as
        well as the width and height of the viewable region.

        Raises
        ------
        This function may raise an OpenGL context-specific error if incorrect
        parameters are used.
        """
        gl_viewport(self.x, self.y, self.width, self.height)


class TestGLMesh:
    """
    Representation of a GL mesh with vertices, optional indices, and attributes.

    This class allows for the creation and management of a graphical mesh,
    including the specification of vertices, optional indices, and associated
    attributes for rendering purposes. It provides methods to add attributes
    to the mesh and handle its drawing using OpenGL.

    Attributes:
        vertices (Any): The vertices of the mesh as provided by the user.
        indices (Optional[Any]): Optional indices for indexed rendering,
            allowing for more efficient rendering of shared vertices.
        attributes (list[GLAttributeArray]): A list of attribute arrays
            associated with the mesh, representing the additional data
            (e.g., colors, texture coordinates) needed for rendering.

    """

    def __init__(self, vertices, indices=None):
        self.vertices = vertices
        self.indices = indices
        self.attributes: list[GLAttributeArray] = []

    def add_attribute(self, attr: GLAttributeArray):
        """
        Adds a GLAttributeArray instance to the attributes list.

        Attributes represent specific data or configuration required for the
        functional operation of the object. This method allows adding new
        attributes dynamically to the internal list.

        Parameters:
            attr (GLAttributeArray): The attribute object to add to the list.
        """
        self.attributes.append(attr)

    def draw(self):
        """
        Draw the object using the attributes and indices provided. This method prepares
        and manages OpenGL drawing by enabling necessary vertex attributes and rendering
        either indexed or non-indexed primitives based on the presence of indices.

        Raises
        ------
        RuntimeError
            If an OpenGL error occurs during the drawing process.
        """
        for attr in self.attributes:
            attr.enable_legacy(GLClientState.VERTEX)  # refine mapping

        if self.indices is not None:
            gl_draw_elements(
                len(self.indices),
                GLIndexType.UNSIGNED_INT,
                GLDrawMode.TRIANGLES,
                pointer=self.indices,
            )


@dataclass
class DrawCommand:
    """
    Represents a command for drawing a mesh with optional rendering parameters.

    This class serves as a utility to encapsulate mesh drawing operations alongside
    related rendering state, texture, and mode settings. It integrates with a rendering
    backend to facilitate the execution of drawing commands.

    Attributes:
        mesh (Any): The mesh object to be drawn. Must support a `draw` method or be used
            with a backend capable of drawing it.
        mode (int | None): Optional drawing mode. Determines how the mesh should be
            rendered. Not all rendering backends require this attribute.
        texture (GLTextureDriver | int | None): Optional texture or reference to a texture.
            If specified, the texture is bound before drawing the mesh.
        state (RenderState | None): Optional rendering state to apply before executing the
            drawing command.

    Methods:
        execute(backend: Any):
            Executes the drawing command by applying the rendering state, binding the texture,
            and invoking the appropriate backend-specific draw operation.

    """

    mesh: Any
    mode: int | None = None
    texture: GLTextureDriver | int | None = None
    state: RenderState | None = None

    def execute(self, backend: Any):
        if self.state is not None:
            if hasattr(backend, "apply_state"):
                backend.apply_state(self.state)
            else:
                RenderStateApplier(backend).apply(self.state)

        if self.texture:
            if isinstance(self.texture, int) and hasattr(backend, "textures"):
                backend.textures.bind_texture(self.texture)
            elif isinstance(self.texture, int) and hasattr(backend, "bind_texture"):
                backend.bind_texture(self.texture)
            elif hasattr(self.texture, "bind"):
                self.texture.bind()

        if self.mode is not None and hasattr(backend, "geometry"):
            backend.geometry.draw_mesh(self.mesh, self.mode)
        elif self.mode is not None and hasattr(backend, "draw_mesh"):
            backend.draw_mesh(self.mesh, self.mode)
        elif hasattr(self.mesh, "draw"):
            self.mesh.draw()
        else:
            raise TypeError(
                "DrawCommand requires a mode/backend draw_mesh or a drawable mesh."
            )


@dataclass
class GLClipPlaneState:
    """gl Clipping Plane State"""

    enabled0: bool = False
    enabled1: bool = False
    plane0: np.ndarray = False
    plane1: np.ndarray = False

    def apply(self, state: GLStateManager):
        state.set_enabled(GLCapability.CLIP_DISTANCE0, self.enabled0)
        state.set_enabled(GLCapability.CLIP_DISTANCE1, self.enabled1)


__all__ = [
    "BlendState",
    "DepthState",
    "DrawCommand",
    "GLAttributeArray",
    "GLClipPlaneState",
    "GLStateManager",
    "GLVertexBuffer",
    "GLViewport",
    "RasterState",
    "RenderState",
    "RenderStateApplier",
    "TestGLMesh",
    "gl_value",
]
