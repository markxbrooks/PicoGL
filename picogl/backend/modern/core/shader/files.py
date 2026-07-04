from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ShaderFiles:
    """GLSL source file names."""
    vertex: str | Path
    fragment: str | Path
    glsl_dir: str | Path

    def __post_init__(self):
        object.__setattr__(self, "vertex", Path(self.vertex))
        object.__setattr__(self, "fragment", Path(self.fragment))
        object.__setattr__(self, "glsl_dir", Path(self.glsl_dir))