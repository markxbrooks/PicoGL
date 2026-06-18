"""
Applyable State
"""

class Applyable:
    """Applyable state"""
    def __init__(self):
        self._current = None

    def apply(self, state):
        if self._current is not None and self._is_same(self._current, state):
            return
        self._do_apply(state)
        self._current = state

    def _is_same(self, old, new) -> bool:
        return old == new

    def _do_apply(self, state):
        raise NotImplementedError
