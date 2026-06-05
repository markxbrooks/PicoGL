from contextlib import contextmanager
from pathlib import Path
from typing import Any

import numpy as np
from OpenGL.raw.GL.ARB.internalformat_query2 import GL_TEXTURE_2D
from OpenGL.raw.GL.VERSION.GL_1_0 import glEnable, glDisable
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture

from elmo.ui.widgets.gl.renderer.legacy import RESOURCE_DIR


@contextmanager
def gl_texture_binding(texture_gl_id: int | None):
    try:
        if texture_gl_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_gl_id)
        yield
    finally:
        if texture_gl_id is not None:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)


def get_texture_path(texture_name: str) -> Path:
    """Return absolute path to a texture."""
    return RESOURCE_DIR / texture_name


def create_checkerboard(texture_data: np.ndarray[Any, Any], texture_size: int):
    """Create a checkerboard pattern"""
    for y in range(texture_size):
        for x in range(texture_size):
            if (x // 8 + y // 8) % 2 == 0:
                # Light blue
                texture_data[y, x] = [100, 150, 255]
            else:
                # Dark blue
                texture_data[y, x] = [50, 100, 200]


def create_checkerboard_array(texture_size: int) -> np.ndarray:
    """Create fallback RGB checkerboard texture data."""
    texture_data = np.zeros((texture_size, texture_size, 3), dtype=np.uint8)
    create_checkerboard(texture_data, texture_size)
    return texture_data


class TextureManager:
    """TextureManager"""

    def __init__(self, backend):
        self.backend = backend
        self._textures: dict[str, int] = {}
        self._timestamps: dict[str, float] = {}

    def get(self, name: str) -> int:
        path = get_texture_path(name)

        if not path.exists():
            return self._get_fallback(name)

        mtime = path.stat().st_mtime

        # Reload only if changed
        if name not in self._textures or self._timestamps.get(name) != mtime:
            self._reload(name, path, mtime)

        return self._textures[name]

    def _reload(self, name: str, path: Path, mtime: float):
        from PIL import Image

        # Delete old GPU texture (critical)
        if name in self._textures:
            self.backend.delete_texture(self._textures[name])

        with Image.open(path) as image:
            image = image.convert("RGB")
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

            texture_id = self.backend.create_texture(
                width=image.width,
                height=image.height,
                data=image.tobytes(),
            )

        self._textures[name] = texture_id
        self._timestamps[name] = mtime

    def _get_fallback(self, name: str) -> int:
        if "__fallback__" not in self._textures:
            data = create_checkerboard_array(64)

            tex = self.backend.create_texture(
                width=64,
                height=64,
                data=data.tobytes(),
            )
            self._textures["__fallback__"] = tex

        return self._textures["__fallback__"]
