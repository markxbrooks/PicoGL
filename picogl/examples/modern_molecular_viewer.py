"""
Molecular Viewer with PDB Support and MolViewSpec Integration

Demonstrates:
1. Loading PDB files via PDBLoader
2. Drawing atoms (points) and bonds (lines) with PicoGL / GLUT
3. Exporting MolViewSpec JSON
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401

_EXAMPLES_DIR = Path(__file__).resolve().parent
_PICOGL_ROOT = _EXAMPLES_DIR.parents[1]
if str(_PICOGL_ROOT) not in sys.path:
    sys.path.insert(0, str(_PICOGL_ROOT))
if str(_EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_DIR))

from utils.molecular_glut_window import MolecularRenderWindow, MolecularViewer


def main() -> None:
    pdb_path = str(_EXAMPLES_DIR / "data" / "2VUG.pdb")

    try:
        viewer = MolecularViewer(pdb_path)
        viewer.export_molviewspec("output.molviewspec")

        render_window = MolecularRenderWindow(
            molecular_viewer=viewer,
            width=1024,
            height=768,
            title="Molecular Viewer - PDB Structure",
            glsl_dir=_EXAMPLES_DIR / "glsl" / "tu01",
        )
        render_window.run()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTo use this example:")
        print("1. Place a PDB file in the data/ directory")
        print("2. Update the pdb_path variable in main()")
        print("3. Run the script again")
        print("\nExample PDB files can be downloaded from:")
        print("- RCSB PDB: https://www.rcsb.org/")
        print("- AlphaFold DB: https://alphafold.ebi.ac.uk/")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
