"""
This module defines dataclasses for managing GLSL shader source file paths.

It provides structures to encapsulate the vertex and fragment shader file
names, as well as their associated directory. The paths are converted to
`Path` objects to facilitate file path manipulations.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ShaderFiles:
    vertex: str | Path
    fragment: str | Path
    glsl_dir: str | Path

    def __post_init__(self):
        glsl_dir = Path(self.glsl_dir)

        object.__setattr__(self, "glsl_dir", glsl_dir)
        object.__setattr__(self, "vertex", glsl_dir / self.vertex)
        object.__setattr__(self, "fragment", glsl_dir / self.fragment)
