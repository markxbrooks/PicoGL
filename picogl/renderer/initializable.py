"""
Initializ class
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