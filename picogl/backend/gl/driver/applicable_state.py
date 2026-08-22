"""
Applicable State
"""
from typing import Generic, T


class ApplicableState(Generic[T]):
    """Applicable State"""

    def __init__(self):
        self._current: T = None

    def apply(self, state: T):
        prev = self._current
        if prev is not None and self._is_same(prev, state):
            return
        self._do_apply(state, prev)
        self._current = state

    def _do_apply(self, state: T, prev: T):
        raise NotImplementedError

    def _is_same(self, old: T, new: T) -> bool:
        raise NotImplementedError
