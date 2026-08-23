"""OpenGL state helpers and scoped context managers."""

from __future__ import annotations

from typing import Any

# Eager imports of scoped pull backend.gl.api, which imports GLTexture and can
# circular-import picogl.texture.gltexture. Expose helpers lazily instead.

__all__ = ["gl_disabled", "enabled", "gl_capability", "gl_shader_bound"]


def __getattr__(name: str) -> Any:
    if name in ("gl_disabled", "enabled", "gl_capability"):
        from picogl.backend.gl.state import scoped

        return getattr(scoped, name)
    if name == "gl_shader_bound":
        from picogl.backend.gl.state.shader import gl_shader_bound

        return gl_shader_bound
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
