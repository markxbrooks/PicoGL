"""
Qt Legacy Molecular Viewer for PDB Files

Loads a PDB, extracts C-alpha atoms, and displays them with legacy OpenGL.
Geometry is compiled into display lists once; paintGL only applies the camera.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import numpy as np
from molib.core.constants import MoLibConstant
from PySide6.QtCore import Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from picogl.backend.geometry import LegacyBinding
from picogl.backend.gl.api.color import gl_color_rgb
from picogl.backend.gl.api.legacy.callist import gl_call_list
from picogl.backend.gl.api.legacy.display_list import (
    GLLegacyListMode,
    gl_end_list,
    gl_gen_lists,
    gl_new_list,
)
from picogl.backend.gl.api.legacy.matrix import gl_pushed_matrix
from picogl.backend.gl.api.legacy.rotate import gl_rotate_vec3
from picogl.backend.gl.backend import GLBackend
from picogl.backend.gl.enums import GLDrawMode
from picogl.backend.gl.enums.legacy.scale import gl_translate_f, gl_translate_vec3
from picogl.backend.gl.state.immediate import gl_immediate_drawing
from picogl.backend.modern.core.setup.lighting import gl_initialize_background
from picogl.core.draw.line import gl_legacy_draw_line
from picogl.core.draw.sphere import (
    draw_latitude_band_connectors,
    draw_latitude_band_filled,
    draw_latitude_ring_wireframe,
)
from picogl.core.geometry.sphere import generate_ring, latitude_for_stack
from picogl.core.rgbcolor import RGBAColor, RGBColor
from picogl.core.setup import gl_setup_lighting, gl_setup_materials
from picogl.core.setup.view import gl_setup_view
from picogl.core.vec3 import Vec3
from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow

_EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
if _EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, _EXAMPLES_DIR)

from utils.pdb_loader import PDBLoader  # noqa: E402

CHAIN_COLORS = {
    "A": RGBColor.GREEN,
    "B": RGBColor.BLUE,
}

ZOOM_SCALE_FACTOR = -50.0
SPHERE_RADIUS = 0.5
SPHERE_SLICES = 8
SPHERE_STACKS = 6


class QtLegacyMolecularViewer(QOpenGLWidget):
    """Qt OpenGL widget for Cα spheres/bonds with legacy OpenGL display lists."""

    def __init__(self, pdb_path: str, parent=None):
        super().__init__(parent)
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.calpha_atoms: list = []
        self.calpha_positions: np.ndarray | None = None
        self.calpha_bonds: list[tuple[int, int]] = []
        self.calpha_colors: list[RGBColor] = []
        self.calpha_bond_colors: list[RGBColor] = []
        self.backend = GLBackend(binding=LegacyBinding())

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 1.0
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.x_axis_matrix = Vec3(1.0, 0.0, 0.0)
        self.y_axis_matrix = Vec3(0.0, 1.0, 0.0)

        self.last_mouse_pos = None
        self.mouse_pressed = False
        self.wireframe_mode = False

        self._sphere_display_list: int | None = None
        self._molecule_display_list: int | None = None

        self._load_pdb_structure()

    def initializeGL(self) -> None:
        gl_initialize_background(RGBAColor.BLACK)
        gl_setup_lighting()
        gl_setup_materials()
        self._create_sphere_display_list()
        self._create_molecule_display_list()

    def resizeGL(self, width: int, height: int) -> None:
        self.backend.legacy.set_view(height, width)

    def paintGL(self) -> None:
        gl_setup_view()
        self._apply_camera_transformations()
        if self._molecule_display_list is not None:
            gl_call_list(self._molecule_display_list)

    def _load_pdb_structure(self) -> None:
        print(f"Loading PDB structure from: {self.pdb_path}")
        try:
            self.pdb_loader = PDBLoader(self.pdb_path)
            structure = self.pdb_loader.structure
            self._extract_calpha_atoms(structure)
            self._convert_calpha_to_np_array()
            self._build_calpha_colors()
            self._generate_calpha_bonds()
            self._build_calpha_bond_colors()
            self._center_positions()
            self._log_pdb_structure(structure)
        except Exception as e:
            print(f"Error loading PDB file: {e}")
            raise

    def _log_pdb_structure(self, structure) -> None:
        print(f"✓ Found {len(self.calpha_atoms)} C-alpha atoms")
        print(f"✓ Structure: {structure.title}")
        print(f"✓ Chains: {structure.chains}")

    def _extract_calpha_atoms(self, structure) -> None:
        self.calpha_atoms = [
            atom
            for atom in structure.atoms
            if atom.name.strip() == MoLibConstant.PEPTIDE_CHAIN_ATOMNAME
        ]

    def _convert_calpha_to_np_array(self) -> None:
        self.calpha_positions = np.array(
            [[atom.x, atom.y, atom.z] for atom in self.calpha_atoms],
            dtype=np.float32,
        )

    def _build_calpha_colors(self) -> None:
        self.calpha_colors = [
            CHAIN_COLORS.get(atom.chain_id, RGBColor.WHITE)
            for atom in self.calpha_atoms
        ]

    def _build_calpha_bond_colors(self) -> None:
        self.calpha_bond_colors = [
            self.calpha_colors[i] for i, _ in self.calpha_bonds
        ]

    def _center_positions(self) -> None:
        if self.calpha_positions is None or len(self.calpha_positions) == 0:
            return
        center = np.mean(self.calpha_positions, axis=0).astype(np.float32)
        self.calpha_positions -= center

    def _generate_calpha_bonds(self) -> None:
        self.calpha_bonds = []
        chain_atoms = self._group_atoms_by_chain()
        for _chain_id, atoms in chain_atoms.items():
            atoms.sort(key=lambda x: x[1].res_seq)
            for i in range(len(atoms) - 1):
                idx1, atom1 = atoms[i]
                idx2, atom2 = atoms[i + 1]
                if atom2.res_seq == atom1.res_seq + 1:
                    self.calpha_bonds.append((idx1, idx2))
        print(f"✓ Generated {len(self.calpha_bonds)} C-alpha bonds")

    def _group_atoms_by_chain(self) -> dict[Any, list]:
        chain_atoms: dict[Any, list] = {}
        for i, atom in enumerate(self.calpha_atoms):
            chain_atoms.setdefault(atom.chain_id, []).append((i, atom))
        return chain_atoms

    def _create_sphere_display_list(self) -> None:
        list_id = gl_gen_lists(1)
        gl_new_list(list_id, GLLegacyListMode.COMPILE)
        self._emit_sphere_geometry(SPHERE_RADIUS, SPHERE_SLICES, SPHERE_STACKS)
        gl_end_list()
        self._sphere_display_list = list_id

    def _emit_sphere_geometry(
        self, radius: float, slices: int, stacks: int
    ) -> None:
        for stack in range(stacks):
            lat0 = latitude_for_stack(stack, stacks)
            lat1 = latitude_for_stack(stack + 1, stacks)
            ring0 = generate_ring(radius, lat0, slices)
            ring1 = generate_ring(radius, lat1, slices)
            if not self.wireframe_mode:
                draw_latitude_band_filled(ring0, ring1)
            draw_latitude_ring_wireframe(ring0)
            draw_latitude_band_connectors(ring0, ring1)

    def _draw_sphere(self) -> None:
        if self._sphere_display_list is not None:
            gl_call_list(self._sphere_display_list)

    def _create_molecule_display_list(self) -> None:
        list_id = gl_gen_lists(1)
        gl_new_list(list_id, GLLegacyListMode.COMPILE)
        self._build_calpha_atoms_geometry()
        self._build_calpha_bonds_geometry()
        gl_end_list()
        self._molecule_display_list = list_id

    def _rebuild_display_lists(self) -> None:
        self._create_sphere_display_list()
        self._create_molecule_display_list()

    def _build_calpha_atoms_geometry(self) -> None:
        if self.calpha_positions is None:
            return
        for pos, color in zip(self.calpha_positions, self.calpha_colors):
            gl_color_rgb(color)
            with gl_pushed_matrix():
                gl_translate_f(float(pos[0]), float(pos[1]), float(pos[2]))
                self._draw_sphere()

    def _build_calpha_bonds_geometry(self) -> None:
        if not self.calpha_bonds or self.calpha_positions is None:
            return
        with gl_immediate_drawing(GLDrawMode.LINES):
            for (i, j), color in zip(self.calpha_bonds, self.calpha_bond_colors):
                gl_color_rgb(color)
                gl_legacy_draw_line(
                    self.calpha_positions[i],
                    self.calpha_positions[j],
                )

    def _apply_camera_transformations(self) -> None:
        gl_translate_vec3(
            Vec3(
                self.translation_x,
                self.translation_y,
                ZOOM_SCALE_FACTOR * self.zoom,
            )
        )
        gl_rotate_vec3(self.rotation_x, self.x_axis_matrix)
        gl_rotate_vec3(self.rotation_y, self.y_axis_matrix)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event) -> None:
        if self.mouse_pressed and self.last_mouse_pos:
            current_pos = event.position().toPoint()
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.last_mouse_pos = current_pos
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.zoom *= zoom_factor
        self.zoom = max(0.1, min(10.0, self.zoom))
        self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_R:
            self.rotation_x = 0.0
            self.rotation_y = 0.0
            self.zoom = 1.0
            self.translation_x = 0.0
            self.translation_y = 0.0
            self.update()
        elif event.key() == Qt.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            print(f"Wireframe mode: {'ON' if self.wireframe_mode else 'OFF'}")
            self._rebuild_display_lists()
            self.update()
        elif event.key() == Qt.Key_Escape:
            self.close()


class LegacyMolecularViewerWindow(LegacyQtObjectWindow):
    """Main window hosting the Cα OpenGL widget."""

    def __init__(self, object_file_path: str | None = None):
        self._pdb_path = object_file_path
        super().__init__(parent=None)
        self.object_file_path = object_file_path
        self.gl_widget = None

    def ui_init(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.set_layout(self.layout)

    def init_ui(self) -> None:
        self.setWindowTitle(
            "Qt Legacy Molecular Viewer - 2VUG C-alpha "
            "(Chain A: Green, Chain B: Blue)"
        )
        self.setGeometry(100, 100, 1200, 800)

    def set_layout(self, layout) -> None:
        info_label = QLabel(
            "2VUG PDB Structure - C-alpha Atoms "
            "(Chain A: Green, Chain B: Blue)"
        )
        info_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px;"
        )

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        upper_widget = QWidget()
        upper_layout = QHBoxLayout()
        upper_widget.setLayout(upper_layout)
        upper_layout.addWidget(info_label)

        lower_widget = QWidget()
        lower_layout = QVBoxLayout()
        splitter.addWidget(upper_widget)
        splitter.addWidget(lower_widget)
        splitter.setSizes([200, 800])
        lower_widget.setLayout(lower_layout)

        controls_layout = QHBoxLayout()
        reset_button = QPushButton("Reset View (R)")
        reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(reset_button)
        info_button = QPushButton("Show Info")
        info_button.clicked.connect(self.show_info)
        controls_layout.addWidget(info_button)
        controls_layout.addStretch()
        upper_layout.addLayout(controls_layout)

        pdb_path = getattr(self, "_pdb_path", None) or self.object_file_path
        self.gl_widget = QtLegacyMolecularViewer(pdb_path)
        lower_layout.addWidget(self.gl_widget)

        instructions = QLabel(
            "Controls:\n"
            "• Left mouse: Rotate\n"
            "• Mouse wheel: Zoom\n"
            "• R key: Reset view\n"
            "• W key: Toggle wireframe/filled\n"
            "• ESC: Exit\n"
            "• Chain A: Green, Chain B: Blue"
        )
        instructions.setStyleSheet(
            "font-size: 12px; padding: 10px; background-color: #f0f0f0;"
        )
        upper_layout.addWidget(instructions)

    def reset_view(self) -> None:
        if self.gl_widget is None:
            return
        self.gl_widget.rotation_x = 0.0
        self.gl_widget.rotation_y = 0.0
        self.gl_widget.zoom = 1.0
        self.gl_widget.translation_x = 0.0
        self.gl_widget.translation_y = 0.0
        self.gl_widget.update()

    def show_info(self) -> None:
        widget = self.gl_widget
        if widget is None or widget.pdb_loader is None:
            return
        structure = widget.pdb_loader.structure
        info_text = (
            f"Structure: {structure.title}\n"
            f"C-alpha atoms: {len(widget.calpha_atoms)}\n"
            f"C-alpha bonds: {len(widget.calpha_bonds)}\n"
            f"Chains: {', '.join(structure.chains)}\n"
            f"Total atoms: {len(structure.atoms)}"
        )
        QMessageBox.information(self, "Structure Information", info_text)


def main() -> int:
    app = QApplication(sys.argv)
    pdb_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "2VUG.pdb")
    )
    print(pdb_path)
    if not os.path.exists(pdb_path):
        print(f"Error: PDB file not found at {pdb_path}")
        return 1
    window = LegacyMolecularViewerWindow(object_file_path=pdb_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
