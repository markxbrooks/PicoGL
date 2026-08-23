"""
Molecular Viewer with PDB Support and MolViewSpec Integration

This example demonstrates how to:
1. Load PDB files using the PDBLoader
2. Visualize molecular structures with PicoGL
3. Export to MolViewSpec format for portable viewing
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo roots on sys.path before any OpenGL / picogl imports.
_EXAMPLES_DIR = Path(__file__).resolve().parent
_PICOGL_ROOT = _EXAMPLES_DIR.parents[1]
_ELMO_ROOT_CANDIDATES = (
    Path(os.environ["ELMO_ROOT"]) if os.environ.get("ELMO_ROOT") else None,
    _PICOGL_ROOT.parent / "ElMo",
    Path.home() / "projects" / "ElMo",
)
_ELMO_ROOT = next(
    (p for p in _ELMO_ROOT_CANDIDATES if p is not None and p.is_dir()),
    Path.home() / "projects" / "ElMo",
)
_ELMO_GLSL = _ELMO_ROOT / "elmo" / "glsl" / "src"
if str(_PICOGL_ROOT) not in sys.path:
    sys.path.insert(0, str(_PICOGL_ROOT))
# examples/ so ``utils.pdb_loader`` resolves
if str(_EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES_DIR))
# ElMo GLSL is read from disk only — do not add ElMo to sys.path (avoids PySide6).

# freeglut creates GLX contexts; under Wayland PyOpenGL may pick EGL first.
if sys.platform.startswith("linux"):
    os.environ.setdefault("PYOPENGL_PLATFORM", "glx")

import picogl.ui.backend.glut.prefer_glut_platform  # noqa: F401

import numpy as np
from OpenGL.GL import *
from utils.pdb_loader import PDBLoader

from picogl.backend.gl.api.enable import gl_enable, gl_enable_capability_list
from picogl.backend.gl.capability import GLPipelineCapability
from picogl.backend.gl.enums.point_size import (
    GLLegacyPointCapability,
    GLPointCapability,
)
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.globals import PICOGL_SHADER_SRC_DIRECTORY
from picogl.renderer import MeshData
from picogl.shaders.registry import ShaderRegistry
from picogl.shaders.type import ShaderType
from picogl.ui.backend.glut.window.object import RenderWindow


def _molecular_shader_directory() -> Path:
    """Prefer ElMo molecular GLSL tree when present; else PicoGL shader src."""
    if _ELMO_GLSL.is_dir() and (_ELMO_GLSL / "atoms" / "vertex.glsl").is_file():
        return _ELMO_GLSL
    return Path(PICOGL_SHADER_SRC_DIRECTORY)


class MolecularViewer:
    """Molecular structure viewer with PDB support"""

    def __init__(self, pdb_path: str):
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.atom_data = None
        self.bond_data = None

        # Load the PDB structure
        self._load_structure()

        # Initialize shaders (needs GL context for compile — deferred until window)
        self.shader_registry = ShaderRegistry(
            shader_directory=_molecular_shader_directory()
        )
        self._shaders_loaded = False

    def ensure_shaders_loaded(self) -> None:
        """Compile shaders once an OpenGL context exists."""
        if self._shaders_loaded:
            return
        self._load_shaders()
        self._shaders_loaded = True

    def _load_structure(self):
        """Load PDB structure and convert to PicoGL format"""
        print(f"Loading PDB structure from: {self.pdb_path}")
        self.pdb_loader = PDBLoader(self.pdb_path)

        # Convert to PicoGL data
        picogl_data = self.pdb_loader.to_picogl_data()

        self.atom_data = picogl_data["atoms"]
        self.bond_data = picogl_data["bonds"]

        print(
            f"Loaded {self.atom_data['count']} atoms and {self.bond_data['count']} bonds"
        )
        print(f"Residues: {len(picogl_data['residues'])}")
        print(f"Chains: {picogl_data['chains']}")

    def _load_shaders(self):
        """Load molecular visualization shaders"""
        print("Loading molecular visualization shaders...")
        print(f"Shader directory: {self.shader_registry.shader_directory}")

        for shader_type in ShaderType:
            program = self.shader_registry.load_and_add(shader_type)
            if program is not None:
                print(f"Loaded shader: {shader_type}")
            else:
                print(f"Warning: Could not load shader {shader_type}")

    def create_atom_mesh(self) -> MeshData:
        """Create mesh data for atoms (spheres)"""
        if not self.atom_data:
            raise ValueError("No atom data loaded")

        # For now, we'll represent atoms as points
        # In a full implementation, you'd generate sphere meshdata
        vertices = np.array(self.atom_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        colors = np.array(self.atom_data["colors"], dtype=np.float32).reshape(-1, 3)

        # Create indices for point rendering
        indices = np.arange(len(vertices), dtype=np.uint32)

        return MeshData.from_raw(
            vertices=vertices.flatten().tolist(),
            colors=colors.flatten().tolist(),
            indices=indices.tolist(),
        )

    def create_bond_mesh(self) -> MeshData:
        """Create mesh data for bonds (lines)"""
        if not self.bond_data:
            raise ValueError("No bond data loaded")

        # Bonds are already in line format (pairs of vertices)
        vertices = np.array(self.bond_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        colors = np.array(self.bond_data["colors"], dtype=np.float32).reshape(-1, 3)

        # Create indices for line rendering
        indices = np.arange(len(vertices), dtype=np.uint32)

        return MeshData.from_raw(
            vertices=vertices.flatten().tolist(),
            colors=colors.flatten().tolist(),
            indices=indices.tolist(),
        )

    def export_molviewspec(self, output_path: str):
        """Export the structure to MolViewSpec format"""
        if self.pdb_loader:
            molviewspec = self.pdb_loader.to_molviewspec()

            import json

            with open(output_path, "w") as f:
                json.dump(molviewspec, f, indent=2)

            print(f"Exported MolViewSpec to: {output_path}")
        else:
            print("No PDB structure loaded to export")


class MolecularRenderWindow(RenderWindow):
    """Specialized render window for molecular visualization"""

    def __init__(self, molecular_viewer: MolecularViewer, **kwargs):
        self.molecular_viewer = molecular_viewer
        self.atom_mesh = None
        self.bond_mesh = None

        # Create meshes
        self.atom_mesh = molecular_viewer.create_atom_mesh()
        self.bond_mesh = molecular_viewer.create_bond_mesh()

        super().__init__(**kwargs)

    def initialize(self):
        """Initialize the molecular viewer"""
        super().initialize()
        self.molecular_viewer.ensure_shaders_loaded()

        # Set up molecular-specific rendering
        self._setup_molecular_rendering()

    def _setup_molecular_rendering(self):
        """Set up molecular visualization specific rendering"""
        # Enable point sprites for atoms
        gl_enable_capability_list(
            [
                GLLegacyPointCapability.POINT_SPRITE,
                GLPointCapability.PROGRAM_POINT_SIZE,
            ]
        )

        # Set point size for atoms
        glPointSize(8.0)

        # Enable line smoothing for bonds
        gl_enable(GLPipelineCapability.LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(2.0)

    def render(self):
        """Render the molecular structure"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Render bonds first (so they appear behind atoms)
        if self.bond_mesh:
            self._render_bonds()

        # Render atoms on top
        if self.atom_mesh:
            self._render_atoms()

    def _render_atoms(self):
        """Render atoms as points"""
        if not self.atom_mesh:
            return

        # Use the atoms shader if available
        atoms_shader = self.molecular_viewer.shader_registry.get(ShaderType.ATOMS)
        if atoms_shader:
            atoms_shader.bind()

            # Set uniforms
            atoms_shader.uniform("mvp_matrix", self.context.mvp_matrix)
            atoms_shader.uniform("point_size", 8.0)

            # Render atoms
            self._render_mesh(self.atom_mesh, GL_POINTS)

            atoms_shader.unbind()
        else:
            # Fallback to basic rendering
            self._render_mesh(self.atom_mesh, GL_POINTS)

    def _render_bonds(self):
        """Render bonds as lines"""
        if not self.bond_mesh:
            return

        # Use the bonds shader if available
        bonds_shader = self.molecular_viewer.shader_registry.get(ShaderType.BONDS)
        if bonds_shader:
            bonds_shader.bind()

            # Set uniforms
            bonds_shader.uniform("mvp_matrix", self.context.mvp_matrix)
            bonds_shader.uniform("line_width", 2.0)

            # Render bonds
            self._render_mesh(self.bond_mesh, GL_LINES)

            bonds_shader.unbind()
        else:
            # Fallback to basic rendering
            self._render_mesh(self.bond_mesh, GL_LINES)

    def _render_mesh(self, mesh: MeshData, mode: int):
        """Render a mesh with the given OpenGL mode"""
        # Create VAO for this mesh
        vao = VertexArrayObject()

        # Add vertex buffer
        vao.add_vbo(index=0, data=np.array(mesh.vertices, dtype=np.float32), size=3)

        # Add colour buffer if available
        if hasattr(mesh, "colors") and mesh.colors:
            vao.add_vbo(index=1, data=np.array(mesh.colors, dtype=np.float32), size=3)

        # Add index buffer if available
        if hasattr(mesh, "indices") and mesh.indices:
            vao.add_vbo(index=2, data=np.array(mesh.indices, dtype=np.uint32), size=1)
            vao.draw(mode=mode, index_count=len(mesh.indices))
        else:
            vao.draw(mode=mode, index_count=len(mesh.vertices) // 3)


def main():
    """Main function to demonstrate molecular viewing"""
    # Example PDB file path - you'll need to provide your own PDB file
    pdb_path = str(_EXAMPLES_DIR / "data" / "2VUG.pdb")

    try:
        # Create molecular viewer
        viewer = MolecularViewer(pdb_path)

        # Export to MolViewSpec
        viewer.export_molviewspec("output.molviewspec")

        # Create render window
        render_window = MolecularRenderWindow(
            molecular_viewer=viewer,
            width=1024,
            height=768,
            title="Molecular Viewer - PDB Structure",
            data=viewer.create_atom_mesh(),  # Create atom mesh for base data
            glsl_dir=Path(__file__).parent / "glsl" / "tu01",
        )

        # Initialize and run
        render_window.initialize()
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
