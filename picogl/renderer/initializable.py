"""
Initializable class
"""


class Initializable:
    """Enforces one-time initialization with optional lazy semantics."""

    __slots__ = ("_initialized",)

    def __init__(self):
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        self._do_initialize()
        self._initialized = True

    def _do_initialize(self) -> None:
        """Subclass must implement actual initialization."""
        raise NotImplementedError

    def ensure_initialized(self) -> None:
        """Call before any operation that requires initialization."""
        if not self._initialized:
            self.initialize()

    def require_initialized(self) -> None:
        """Strict check (no auto-init)."""
        if not self._initialized:
            raise RuntimeError(f"{self.__class__.__name__} not initialized")


class Bindable:
    """Enforces one-time binding with optional lazy semantics."""

    __slots__ = ("_bound",)

    def __init__(self):
        self._bound = False

    def bind(self) -> None:
        if self._bound:
            return
        self._do_binding()
        self._bound = True

    def _do_binding(self) -> None:
        raise NotImplementedError

    def ensure_bound(self) -> None:
        if not self._bound:
            self.bind()

    def require_bound(self) -> None:
        if not self._bound:
            raise RuntimeError(f"{self.__class__.__name__} not bound")

    def unbind(self) -> None:
        if not self._bound:
            return
        self._do_unbinding()
        self._bound = False

    def _do_unbinding(self) -> None:
        raise NotImplementedError

    def __enter__(self):
        self.ensure_bound()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()
