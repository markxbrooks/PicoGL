from typing import Protocol


class MeshBackend(Protocol):
    def draw(self, *args, **kwargs): ...
