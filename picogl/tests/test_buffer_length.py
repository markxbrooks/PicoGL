"""Tests for buffer vertex-count helpers."""

import unittest

import numpy as np
from picogl.gpu.buffers.length import (
    drawable_data_length,
    length_from_array_data,
    length_from_vbo,
)
from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType


class _RecordingVBO:
    def __init__(self, data: np.ndarray, *, components: int = 3):
        self.data = data
        self.components = components


class TestBufferLengthHelpers(unittest.TestCase):
    def test_length_from_array_data_2d(self):
        data = np.zeros((5, 3), dtype=np.float32)
        self.assertEqual(length_from_array_data(data), 5)

    def test_length_from_array_data_1d(self):
        data = np.zeros(12, dtype=np.float32)
        self.assertEqual(length_from_array_data(data, components=3), 4)

    def test_length_from_vbo_delegates_to_data_length(self):
        vbo = _RecordingVBO(np.zeros((2, 3), dtype=np.float32))

        class _WithMethod:
            def data_length(self) -> int:
                return 7

        self.assertEqual(length_from_vbo(_WithMethod()), 7)
        self.assertEqual(length_from_vbo(vbo), 2)

    def test_vertex_buffer_group_data_length_uses_position_vbo(self):
        positions = np.zeros((6, 3), dtype=np.float32)

        class _Group:
            named_vbos = {VBOType.VBO: _RecordingVBO(positions)}

            def data_length(self) -> int:
                from picogl.gpu.buffers.length import length_from_vbo

                return length_from_vbo(self.named_vbos[VBOType.VBO])

        group = _Group()
        self.assertEqual(group.data_length(), 6)
        self.assertEqual(drawable_data_length(group), 6)

    def test_vertex_buffer_group_data_length_falls_back_to_index_count(self):
        indices = np.array([0, 1, 2, 3], dtype=np.uint32)

        class _Group:
            index_count = 4
            named_vbos = {}

            def data_length(self) -> int:
                from picogl.gpu.buffers.length import length_from_vbo
                from picogl.gpu.buffers.vertex.vbo.vbo_class import VBOType

                pos = self.named_vbos.get(VBOType.VBO)
                count = length_from_vbo(pos)
                return count if count > 0 else int(self.index_count)

        group = _Group()
        self.assertEqual(group.data_length(), 4)


if __name__ == "__main__":
    unittest.main()
