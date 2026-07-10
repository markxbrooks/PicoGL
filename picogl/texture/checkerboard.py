import numpy as np


def generate_checkerboard_texture() -> tuple[bytes, int, int]:
    """generate_checkerboard_texture"""
    texture_size = 64
    texture_data = np.zeros((texture_size, texture_size, 3), dtype=np.uint8)
    for y in range(texture_size):
        for x in range(texture_size):
            if (x // 8 + y // 8) % 2 == 0:
                texture_data[y, x] = [100, 150, 255]
            else:
                texture_data[y, x] = [50, 100, 200]
    texture_buffer = texture_data.tobytes()
    texture_width = texture_height = texture_size
    return texture_buffer, texture_height, texture_width
