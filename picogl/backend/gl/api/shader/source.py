from __future__ import annotations

from OpenGL.GL import glShaderSource


def gl_shader_source(shader: int, source: str | bytes | list[str]) -> None:
    """
    Replace the source code in a shader object.

    Args:
        shader: OpenGL shader object handle.
        source: GLSL source as a string, bytes, or list of strings.
    """
    if callable(source):
        raise TypeError(
            "gl_shader_source expected GLSL source text, got a callable "
            f"({source!r}). Check that shader loading returns a string, "
            "not a decorator/factory."
        )
    if isinstance(source, (str, bytes)):
        glShaderSource(shader, [source])
    else:
        glShaderSource(shader, source)
