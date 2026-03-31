from functools import wraps

from picogl.shaders.type import ShaderType


def load_shader(shader_type: ShaderType):
    """
    A decorator to load the shader and set the MVP matrix.

    Args:
        shader_type (ShaderType): The type of shader to use.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper that supports both keyword-style and legacy positional calls.

            Expected original signature (after any container like RibbonChainGroup):
                func(ribbon_buffers, shader_manager, mvp_matrix, zoom_scale=None, ...)
            """
            # Prefer explicit keyword arguments when provided
            shader_manager = kwargs.get("shader_manager")
            mvp_matrix = kwargs.get("mvp_matrix")
            zoom_scale = kwargs.get("zoom_scale")

            # Backwards compatibility: allow positional shader_manager / mvp_matrix
            #
            # args layout for draw_ribbon_vao:
            #   0: ribbon_buffers (RibbonChainGroup)
            #   1: shader_manager (ShaderManager)
            #   2: mvp_matrix (glm.mat4 / np.ndarray)
            #   3: optional zoom_scale (float)
            if shader_manager is None and len(args) >= 2:
                shader_manager = args[1]
            if mvp_matrix is None and len(args) >= 3:
                mvp_matrix = args[2]
            if zoom_scale is None and len(args) >= 4:
                zoom_scale = args[3]

            if shader_manager is None or mvp_matrix is None:
                raise ValueError(
                    "shader_manager and mvp_matrix must be provided "
                    "either as keyword arguments or positional parameters."
                )

            # Use the shader and set the MVP matrix
            shader_manager.use_shader_type(
                shader_type=shader_type, mvp_matrix=mvp_matrix, zoom_scale=zoom_scale
            )

            # Execute the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
