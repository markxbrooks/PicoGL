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
            shader_manager = kwargs.get("shader_manager")
            mvp_matrix = kwargs.get("mvp_matrix")
            zoom_scale = kwargs.get("zoom_scale")

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

            shader = shader_manager.use(shader_type)
            if shader is not None:
                shader.set_mvp(mvp_matrix)
                if zoom_scale is not None:
                    shader.set_uniform("zoom_scale", float(zoom_scale))

            return func(*args, **kwargs)

        return wrapper

    return decorator
