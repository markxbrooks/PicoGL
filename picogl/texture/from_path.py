import os

from decologr import Decologr as log
from PIL import Image

from picogl.texture.checkerboard import generate_checkerboard_texture


def load_texture_file_from_path(texture_path: str) -> tuple[bytes, int, int]:
    """load_texture_file_from_path"""
    with Image.open(texture_path) as image:
        converted = image.convert("RGB")
        texture_buffer = converted.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        texture_width, texture_height = image.size
    return texture_buffer, texture_height, texture_width


def load_texture(texture_path: str) -> tuple[bytes, int, int]:
    """load texture from texture path"""
    if os.path.exists(texture_path):
        texture_buffer, texture_height, texture_width = load_texture_file_from_path(
            texture_path
        )
    else:
        log.warning(f"Texture file not found: {texture_path}")
        texture_buffer, texture_height, texture_width = generate_checkerboard_texture()
    return texture_buffer, texture_height, texture_width
