"""Tests for declarative render graph execution."""

import unittest
from unittest.mock import MagicMock

from OpenGL.raw.GL.VERSION.GL_1_0 import GL_RGBA
from picogl.backend.render.executor import RenderGraphExecutor
from picogl.backend.render.graph import DependencyGraph, RenderGraph, topo_sort
from picogl.backend.render.pass_ import RenderPass
from picogl.backend.render.pipeline import RenderPipeline
from picogl.backend.render.resources import FrameResources
from picogl.backend.state import RenderState


class TestRenderGraph(unittest.TestCase):
    def test_topo_sort_orders_dependencies(self):
        order = topo_sort(
            ["geometry", "shadow"],
            {"geometry": {"shadow"}},
        )
        self.assertEqual(order, ["shadow", "geometry"])

    def test_topo_sort_detects_cycles(self):
        with self.assertRaises(ValueError):
            topo_sort(
                ["a", "b"],
                {"a": {"b"}, "b": {"a"}},
            )

    def test_dependency_graph_builds_write_read_edges(self):
        from picogl.backend.render.resources import Texture

        shadow_tex = Texture("shadow", 512, 512, 0)
        scene_tex = Texture("scene", 1920, 1080, GL_RGBA)

        shadow_pass = RenderPass(
            name="shadow",
            state=RenderState(),
            execute_fn=lambda: None,
            writes=[shadow_tex],
        )
        geometry_pass = RenderPass(
            name="geometry",
            state=RenderState(),
            execute_fn=lambda: None,
            reads=[shadow_tex],
            writes=[scene_tex],
        )

        dep = DependencyGraph()
        dep.build([geometry_pass, shadow_pass])
        order = topo_sort([p.name for p in (geometry_pass, shadow_pass)], dep.edges)

        self.assertEqual(order.index("shadow"), 0)
        self.assertEqual(order.index("geometry"), 1)

    def test_render_pipeline_executes_in_order(self):
        backend = MagicMock()
        calls: list[str] = []

        pipeline = RenderPipeline()
        pipeline.add(
            RenderPass("first", RenderState(), execute_fn=lambda: calls.append("first"))
        )
        pipeline.add(
            RenderPass(
                "second", RenderState(), execute_fn=lambda: calls.append("second")
            )
        )
        pipeline.execute(backend)

        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(backend.apply_state.call_count, 2)

    def test_render_graph_executor_applies_state_and_runs_passes(self):
        backend = MagicMock()
        calls: list[str] = []

        graph = RenderGraph()
        graph.add(
            RenderPass(
                "draw",
                RenderState(depth_test=True),
                execute_fn=lambda: calls.append("draw"),
            )
        )

        RenderGraphExecutor(backend).execute(graph)

        self.assertEqual(calls, ["draw"])
        backend.apply_state.assert_called_once()

    def test_frame_resources_create_texture(self):
        resources = FrameResources()
        tex = resources.create_texture("color", 100, 200, GL_RGBA)

        self.assertIs(resources.textures["color"], tex)
        self.assertEqual(tex.width, 100)


if __name__ == "__main__":
    unittest.main()
