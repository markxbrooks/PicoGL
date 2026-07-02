import pytest
from picogl.renderer.base import RendererBase
from picogl.renderer.initializable import Bindable, Initializable


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


class _CountingBindable(Bindable):
    def __init__(self):
        super().__init__()
        self.bind_calls = 0
        self.unbind_calls = 0

    def _do_binding(self) -> None:
        self.bind_calls += 1

    def _do_unbinding(self) -> None:
        self.unbind_calls += 1


def test_bindable_bind_calls_do_binding_once():
    obj = _CountingBindable()

    obj.bind()
    obj.bind()

    assert obj.bind_calls == 1
    assert obj._bound is True


def test_bindable_ensure_and_require_bound():
    obj = _CountingBindable()

    with pytest.raises(RuntimeError):
        obj.require_bound()

    obj.ensure_bound()
    obj.require_bound()

    assert obj.bind_calls == 1


def test_bindable_context_manager_binds_once_and_unbinds():
    obj = _CountingBindable()

    with obj:
        obj.ensure_bound()

    assert obj.bind_calls == 1
    assert obj.unbind_calls == 1
    assert obj._bound is False


def test_bindable_unbind_when_not_bound_is_safe():
    obj = _CountingBindable()

    obj.unbind()

    assert obj.unbind_calls == 0


def test_bindable_importable_from_renderer_package():
    from picogl.renderer import Bindable as ExportedBindable
    from picogl.renderer import Initializable as ExportedInitializable

    assert ExportedBindable is Bindable
    assert ExportedInitializable is Initializable
