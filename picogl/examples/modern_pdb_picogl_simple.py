"""
Simple PDB PicoGL Viewer

Loads a PDB and displays atoms (smooth points) and bonds (lines) using the
same render path as ``modern_molecular_viewer.py`` — not as a single triangle mesh.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo roots on sys.path before any picogl import.
_EXAMPLES_DIR = Path(__file__).resolve().parent
_PICOGL_ROOT = _EXAMPLES_DIR.parents[1]
if str(_PICOGL_ROOT) not in sys.path:
    sys.path.insert(0, str(_PICOGL_ROOT))
if str(_EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_DIR))

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

# Explicit module path — avoids shadowing by another ``molecular_viewer`` on sys.path.
from utils.molecular_glut_window import MolecularRenderWindow, MolecularViewer

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401


def _resolve_pdb_path(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1]).expanduser().resolve()
    default = _EXAMPLES_DIR / "data" / "2VUG.pdb"
    if default.is_file():
        return default
    return Path("data/example.pdb")


def main() -> None:
    pdb_path = _resolve_pdb_path(sys.argv)

    if not pdb_path.is_file():
        print(f"Error: PDB file not found: {pdb_path}")
        print("\nUsage:")
        print(f"  python {Path(sys.argv[0]).name} [path/to/structure.pdb]")
        print("\nExample:")
        print(f"  python {Path(sys.argv[0]).name} data/2VUG.pdb")
        return

    try:
        viewer = MolecularViewer(str(pdb_path))

        render_window = MolecularRenderWindow(
            molecular_viewer=viewer,
            width=800,
            height=600,
            title=f"Molecular Structure - {pdb_path.name}",
            glsl_dir=_EXAMPLES_DIR / "glsl" / "tu01",
            base_dir=_EXAMPLES_DIR,
        )

        print("✓ Created render window")
        print("🎮 Controls:")
        print("  Mouse drag: Rotate view")
        print("  Scroll: Zoom in/out")
        print("  Q: Quit")

        render_window.initialize()
        render_window.initialize()
        render_window.run()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
