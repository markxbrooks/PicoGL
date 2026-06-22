"""
Applyable State
"""


class Applyable:
    """Applyable State"""

    def __init__(self):
        self._current = None

    def apply(self, state):
        prev = self._current
        if prev is not None and self._is_same(prev, state):
            return
        self._do_apply(state, prev)
        self._current = state

    def _do_apply(self, state, prev):
        raise NotImplementedError

    def _is_same(self, old, new) -> bool:
        raise NotImplementedError
