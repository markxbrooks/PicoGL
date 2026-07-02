"""
Cube vertex and color data represented as NumPy arrays.

This module defines two NumPy arrays: CUBE_VERTICES and CUBE_COLORS, which
are used to represent the vertices and corresponding RGB color data of a 3D
cube. The vertex data is defined in 3D space (x, y, z), while the color data
provides RGB values for each vertex. Both arrays are of dtype `float32`.
These arrays are typically utilized in applications like 3D graphics
rendering.

Attributes:
    CUBE_VERTICES (numpy.ndarray): A NumPy array containing 3D coordinates of
        the cube's vertices. Each vertex is represented as three consecutive
        floating-point values (x, y, z). The total shape of the data is
        determined by the number of vertices times 3.
    CUBE_COLORS (numpy.ndarray): A NumPy array containing RGB color values
        for each vertex. Each color is represented as three consecutive
        floating-point values (r, g, b). The total shape of the data matches
        the number of vertices times 3.
"""
import numpy as np

# Cube data (from cube_data.py)
CUBE_VERTICES = np.array(
    [
        -1.0,
        -1.0,
        -1.0,  # 0
        -1.0,
        -1.0,
        1.0,  # 1
        -1.0,
        1.0,
        1.0,  # 2
        1.0,
        1.0,
        -1.0,  # 3
        -1.0,
        -1.0,
        -1.0,  # 4
        -1.0,
        1.0,
        -1.0,  # 5
        1.0,
        -1.0,
        1.0,  # 6
        -1.0,
        -1.0,
        -1.0,  # 7
        1.0,
        -1.0,
        -1.0,  # 8
        1.0,
        1.0,
        -1.0,  # 9
        1.0,
        -1.0,
        -1.0,  # 10
        -1.0,
        -1.0,
        -1.0,  # 11
        -1.0,
        -1.0,
        -1.0,  # 12
        -1.0,
        1.0,
        1.0,  # 13
        -1.0,
        1.0,
        -1.0,  # 14
        1.0,
        -1.0,
        1.0,  # 15
        -1.0,
        -1.0,
        1.0,  # 16
        -1.0,
        -1.0,
        -1.0,  # 17
        -1.0,
        1.0,
        1.0,  # 18
        -1.0,
        -1.0,
        1.0,  # 19
        1.0,
        -1.0,
        1.0,  # 20
        1.0,
        1.0,
        1.0,  # 21
        1.0,
        -1.0,
        -1.0,  # 22
        1.0,
        1.0,
        -1.0,  # 23
        1.0,
        -1.0,
        -1.0,  # 24
        1.0,
        1.0,
        1.0,  # 25
        1.0,
        -1.0,
        1.0,  # 26
        1.0,
        1.0,
        1.0,  # 27
        1.0,
        1.0,
        -1.0,  # 28
        -1.0,
        1.0,
        -1.0,  # 29
        1.0,
        1.0,
        1.0,  # 30
        -1.0,
        1.0,
        -1.0,  # 31
        -1.0,
        1.0,
        1.0,  # 32
        1.0,
        1.0,
        1.0,  # 33
        -1.0,
        1.0,
        1.0,  # 34
        1.0,
        -1.0,
        1.0,  # 35
    ],
    dtype=np.float32,
)

CUBE_COLORS = np.array(
    [
        0.583,
        0.771,
        0.014,  # 0
        0.609,
        0.115,
        0.436,  # 1
        0.327,
        0.483,
        0.844,  # 2
        0.822,
        0.569,
        0.201,  # 3
        0.435,
        0.602,
        0.223,  # 4
        0.310,
        0.747,
        0.185,  # 5
        0.597,
        0.770,
        0.761,  # 6
        0.559,
        0.436,
        0.730,  # 7
        0.359,
        0.583,
        0.152,  # 8
        0.483,
        0.596,
        0.789,  # 9
        0.559,
        0.861,
        0.639,  # 10
        0.195,
        0.548,
        0.859,  # 11
        0.014,
        0.184,
        0.576,  # 12
        0.771,
        0.328,
        0.970,  # 13
        0.406,
        0.615,
        0.116,  # 14
        0.676,
        0.977,
        0.133,  # 15
        0.971,
        0.572,
        0.833,  # 16
        0.140,
        0.616,
        0.489,  # 17
        0.997,
        0.513,
        0.064,  # 18
        0.945,
        0.719,
        0.592,  # 19
        0.543,
        0.021,
        0.978,  # 20
        0.279,
        0.317,
        0.505,  # 21
        0.167,
        0.620,
        0.077,  # 22
        0.347,
        0.857,
        0.137,  # 23
        0.055,
        0.953,
        0.042,  # 24
        0.714,
        0.505,
        0.345,  # 25
        0.783,
        0.290,
        0.734,  # 26
        0.722,
        0.645,
        0.174,  # 27
        0.302,
        0.455,
        0.848,  # 28
        0.225,
        0.587,
        0.040,  # 29
        0.517,
        0.713,
        0.338,  # 30
        0.053,
        0.959,
        0.120,  # 31
        0.393,
        0.621,
        0.362,  # 32
        0.673,
        0.211,
        0.457,  # 33
        0.820,
        0.883,
        0.371,  # 34
        0.982,
        0.099,
        0.879,  # 35
    ],
    dtype=np.float32,
)
