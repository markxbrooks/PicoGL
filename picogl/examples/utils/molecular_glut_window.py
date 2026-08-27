"""
Shared GLUT molecular viewer: atoms as points, bonds as lines.

Used by ``molecular_viewer.py`` and ``pdb_picogl_simple.py``. Never draws atom
positions through ObjectRenderer / GL_TRIANGLES (that produces triangle soup).
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from picogl.backend.gl.api.blending import gl_blend_func
from picogl.backend.gl.api.clear import gl_clear_color
from picogl.backend.gl.api.draw.array import gl_draw_arrays
from picogl.backend.gl.api.enable import gl_disable, gl_enable
from picogl.backend.gl.api.hint import gl_hint
from picogl.backend.gl.api.line import gl_line_width
from picogl.backend.gl.api.point import gl_point_size
from picogl.backend.gl.capability import GLBlendFactor, GLPipelineCapability
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.enums.hint import GLHintMode, GLHintTarget
from picogl.backend.gl.enums.point_size import (
    GLLegacyPointCapability,
    GLPointCapability,
)
from picogl.backend.gl.state.scoped import gl_capability
from picogl.backend.gl.state.shader import gl_shader_bound
from picogl.backend.gl.task.gl_init import legacy_init_gl_list, paint_gl_list
from picogl.backend.modern.core.shader.program import ShaderProgram
from picogl.backend.modern.core.vertex.array.object import VertexArrayObject
from picogl.globals import PICOGL_SHADER_SRC_DIRECTORY
from picogl.renderer import MeshData
from picogl.shaders.registry import ShaderRegistry
from picogl.shaders.type import ShaderType
from picogl.ui.backend.glut.window.object import RenderWindow
from utils.pdb_loader import PDBLoader

_EXAMPLES_DIR = Path(__file__).resolve().parent.parent
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

_ATOM_POINT_SIZE = 6.0
_MOLECULAR_GLSL_DIR = _EXAMPLES_DIR / "glsl" / "molecular"


def _molecular_shader_directory() -> Path:
    """Prefer ElMo molecular GLSL tree when present; else PicoGL shader src."""
    if _ELMO_GLSL.is_dir() and (_ELMO_GLSL / "atoms" / "vertex.glsl").is_file():
        return _ELMO_GLSL
    return Path(PICOGL_SHADER_SRC_DIRECTORY)


class MolecularViewer:
    """Load a PDB and expose PicoGL meshes + optional molecular shaders."""

    def __init__(self, pdb_path: str):
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.atom_data = None
        self.bond_data = None
        self._center = np.zeros(3, dtype=np.float32)
        self._extent = 50.0

        self._load_structure()

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

    def _load_structure(self) -> None:
        print(f"Loading PDB structure from: {self.pdb_path}")
        self.pdb_loader = PDBLoader(self.pdb_path)
        picogl_data = self.pdb_loader.to_picogl_data()

        self.atom_data = picogl_data["atoms"]
        self.bond_data = picogl_data["bonds"]

        positions = np.asarray(self.atom_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        self._center = positions.mean(axis=0).astype(np.float32)
        half = float(np.max(np.linalg.norm(positions - self._center, axis=1)))
        self._extent = max(half, 1.0)

        print(
            f"Loaded {self.atom_data['count']} atoms and {self.bond_data['count']} bonds"
        )
        print(f"Residues: {len(picogl_data['residues'])}")
        print(f"Chains: {picogl_data['chains']}")

    def _load_shaders(self) -> None:
        print("Loading molecular visualization shaders...")
        print(f"Shader directory: {self.shader_registry.shader_directory}")
        for shader_type in (ShaderType.ATOMS, ShaderType.BONDS):
            program = self.shader_registry.load_and_add(shader_type)
            if program is not None:
                print(f"Loaded shader: {shader_type}")
            else:
                print(f"Warning: Could not load shader {shader_type}")

    def create_atom_mesh(self) -> MeshData:
        if not self.atom_data:
            raise ValueError("No atom data loaded")
        vertices = np.asarray(self.atom_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        vertices = vertices - self._center
        colors = np.asarray(self.atom_data["colors"], dtype=np.float32).reshape(-1, 3)
        return MeshData.from_raw(
            vertices=vertices.reshape(-1),
            colors=colors.reshape(-1),
        )

    def create_bond_mesh(self) -> MeshData:
        if not self.bond_data:
            raise ValueError("No bond data loaded")
        vertices = np.asarray(self.bond_data["positions"], dtype=np.float32).reshape(
            -1, 3
        )
        vertices = vertices - self._center
        colors = np.asarray(self.bond_data["colors"], dtype=np.float32).reshape(-1, 3)
        return MeshData.from_raw(
            vertices=vertices.reshape(-1),
            colors=colors.reshape(-1),
        )

    def export_molviewspec(self, output_path: str) -> None:
        if not self.pdb_loader:
            print("No PDB structure loaded to export")
            return
        import json

        with open(output_path, "w") as f:
            json.dump(self.pdb_loader.to_molviewspec(), f, indent=2)
        print(f"Exported MolViewSpec to: {output_path}")


def _mesh_vertex_count(mesh: MeshData) -> int:
    if mesh.vertex_count:
        return int(mesh.vertex_count)
    return int(len(np.asarray(mesh.vertices).reshape(-1, 3)))


def _build_mesh_vao(mesh: MeshData) -> VertexArrayObject:
    """Upload positions + colours for non-indexed glDrawArrays."""
    vao = VertexArrayObject()
    vao.add_vbo(
        index=0,
        data=np.ascontiguousarray(mesh.vertices, dtype=np.float32),
        size=3,
    )
    if mesh.colors is not None and len(mesh.colors):
        vao.add_vbo(
            index=1,
            data=np.ascontiguousarray(mesh.colors, dtype=np.float32),
            size=3,
        )
    return vao


def _enable_blending() -> None:
    """Soft circular points need blending for the smoothstep rim."""
    gl_enable(GLPipelineCapability.BLEND)
    gl_blend_func(GLBlendFactor.SRC_ALPHA, GLBlendFactor.ONE_MINUS_SRC_ALPHA)


class MolecularRenderWindow(RenderWindow):
    """GLUT window that draws atoms as points and bonds as lines."""

    def __init__(self, molecular_viewer: MolecularViewer, **kwargs):
        self.molecular_viewer = molecular_viewer
        self.atom_mesh = molecular_viewer.create_atom_mesh()
        self.bond_mesh = molecular_viewer.create_bond_mesh()
        self.atom_vao: VertexArrayObject | None = None
        self.bond_vao: VertexArrayObject | None = None
        self.atom_point_shader: ShaderProgram | None = None
        self._gl_ready = False

        # ObjectRenderer needs MeshData to compile tu01 bond shaders. Never call
        # renderer.initialize() — that uploads atoms for GL_TRIANGLES (triangle soup).
        kwargs.setdefault("data", self.atom_mesh)
        super().__init__(**kwargs)
        self.renderer.show_model = False

        self.zoom_distance = max(molecular_viewer._extent * 2.5, 20.0)
        self.distance_threshold = max(molecular_viewer._extent * 0.5, 5.0)
        self.sync_zoom_to_context()

    def initializeGL(self) -> None:
        """Load bond shaders only; do not upload atom mesh for triangle drawing."""
        self.backend.execute_gl_tasks(legacy_init_gl_list)
        self.renderer.initialize_shaders()
        self.renderer.show_model = False

    def initialize(self) -> None:
        super().initialize()
        self.molecular_viewer.ensure_shaders_loaded()
        self.atom_vao = _build_mesh_vao(self.atom_mesh)
        self.bond_vao = _build_mesh_vao(self.bond_mesh)
        self._load_atom_point_shader()
        self._setup_molecular_rendering()
        self.calculate_mvp_matrix(self.width, self.height)
        self._gl_ready = True
        self.update()

    def run(self) -> None:
        if not self._gl_ready:
            self.initialize()
        else:
            self.update()
        super().run()

    def _load_atom_point_shader(self) -> None:
        """Circular point sprites (gl_PointCoord discard + soft edge)."""
        self.atom_point_shader = ShaderProgram(
            shader_name="molecular_atom_points",
            vertex_source_file="vertex.glsl",
            fragment_source_file="fragment.glsl",
            glsl_dir=_MOLECULAR_GLSL_DIR,
        )

    def _setup_molecular_rendering(self) -> None:
        gl_enable(GLPipelineCapability.LINE_SMOOTH)
        gl_hint(GLHintTarget.LINE_SMOOTH, GLHintMode.NICEST)
        gl_line_width(1.5)
        _enable_blending()
        gl_enable(GLLegacyPointCapability.POINT_SMOOTH)
        gl_hint(GLHintTarget.POINT_SMOOTH, GLHintMode.NICEST)
        gl_clear_color((0.05, 0.05, 0.08, 1.0))

    def paintGL(self) -> None:
        """Clear, then bonds (lines) and atoms (points) — never triangles."""
        self.renderer.show_model = False
        self.backend.execute_gl_tasks(paint_gl_list)
        if not self._gl_ready:
            return
        if self.bond_vao is not None:
            self._render_bonds()
        if self.atom_vao is not None:
            self._render_atoms()

    def _bond_shader(self):
        """Prefer ObjectRenderer tu01; fall back to ElMo bonds if needed."""
        tu01 = getattr(self.context, "shader", None)
        if tu01 is not None:
            return tu01, "tu01"
        bonds = self.molecular_viewer.shader_registry.get(ShaderType.BONDS)
        if bonds is not None:
            return bonds, "elmo"
        return None, None

    def _bind_uniforms(self, shader, kind: str | None) -> None:
        mvp = self.context.mvp_matrix
        if kind == "elmo":
            model = self.context.model_matrix
            view = self.context.view
            shader.uniform("mvp", mvp)
            shader.uniform("model", model)
            shader.uniform("modelView", view * model)
            shader.uniform("viewPos", self.context.eye_np)
            extent = max(self.molecular_viewer._extent, 1.0)
            zoom_scale = max(self.zoom_distance / (extent * 2.5), 0.25)
            shader.uniform("zoom_scale", float(zoom_scale))
        else:
            shader.uniform("mvp_matrix", mvp)

    def _render_atoms(self) -> None:
        """Draw atoms as smooth circular GL_POINTS."""
        if self.atom_vao is None:
            return
        count = _mesh_vertex_count(self.atom_mesh)
        if count <= 0:
            return

        shader = self.atom_point_shader
        if shader is None:
            shader, kind = self._bond_shader()
            if shader is None:
                return
            with gl_shader_bound(shader):
                self._bind_uniforms(shader, kind)
                gl_disable(GLPointCapability.PROGRAM_POINT_SIZE)
                gl_point_size(_ATOM_POINT_SIZE)
                with self.atom_vao.bound():
                    gl_draw_arrays(count, GLDrawMode.POINTS, first=0)
            return

        with gl_shader_bound(shader):
            with gl_capability(GLPointCapability.PROGRAM_POINT_SIZE, True):
                shader.uniform("mvp_matrix", self.context.mvp_matrix)
                shader.uniform("point_size", float(_ATOM_POINT_SIZE))
                _enable_blending()
                with self.atom_vao.bound():
                    gl_draw_arrays(count, GLDrawMode.POINTS, first=0)

    def _render_bonds(self) -> None:
        shader, kind = self._bond_shader()
        if shader is None or self.bond_vao is None:
            return
        with gl_shader_bound(shader):
            self._bind_uniforms(shader, kind)
            self.bond_vao.draw(
                mode=GLDrawMode.LINES,
                index_count=_mesh_vertex_count(self.bond_mesh),
            )
