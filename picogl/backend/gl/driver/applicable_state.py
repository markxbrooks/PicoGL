"""
Applicable State
"""

from typing import Generic, TypeVar

T = TypeVar("T")


class ApplicableState(Generic[T]):
    """Apply a new state value, distinct from ``Applicable``.

    ``Applicable`` objects apply their own current fields via ``apply()``.
  ``ApplicableState`` subclasses receive an explicit ``state`` argument and
    may cache the last applied value to skip redundant driver calls.
    """

    def __init__(self) -> None:
        self._current: T | None = None

    def apply(self, state: T) -> None:
        prev = self._current
        if prev is not None and self._is_same(prev, state):
            return
        self._do_apply(state, prev)
        self._current = state

    def _do_apply(self, state: T, prev: T | None) -> None:
        raise NotImplementedError

    def _is_same(self, old: T, new: T) -> bool:
        raise NotImplementedError
