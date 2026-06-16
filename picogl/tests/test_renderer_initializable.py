import pytest

from picogl.renderer.base import RendererBase
from picogl.renderer.initializable import Initializable


class _CountingInitializable(Initializable):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def _do_initialize(self):
        self.calls += 1


class _ConcreteRenderer(RendererBase):
    def __init__(self):
        super().__init__()
        self.initialize_calls = 0
        self.draw_calls = 0

    def _do_initialize(self):
        self.initialize_calls += 1

    def _draw_model(self):
        self.draw_calls += 1

    def _draw_selection(self):
        pass


def test_initializable_initialize_calls_do_initialize_once():
    obj = _CountingInitializable()

    obj.initialize()
    obj.initialize()

    assert obj.calls == 1
    assert obj._initialized is True


def test_initializable_ensure_and_require_initialized():
    obj = _CountingInitializable()

    with pytest.raises(RuntimeError):
        obj.require_initialized()

    obj.ensure_initialized()
    obj.require_initialized()

    assert obj.calls == 1


def test_renderer_base_initialize_uses_template_hook_once():
    renderer = _ConcreteRenderer()

    renderer.initialize()
    renderer.initialize()

    assert renderer.initialize_calls == 1
    assert renderer.initialized is True


def test_renderer_base_dispatch_list_stores_draw_callable():
    renderer = _ConcreteRenderer()
    renderer.show_model = True

    dispatch = renderer.dispatch_list

    assert renderer.draw_calls == 0
    assert dispatch == [(True, renderer._draw_model)]
