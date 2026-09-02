"""
Qt Legacy GLMesh Molecular Viewer for PDB Files

This example demonstrates how to:
1. Load PDB files using the PDBLoader
2. Extract C-alpha atoms (CA) from the structure
3. Convert them to PicoGL MeshData format
4. Display them using LegacyGLMesh for rendering
5. Provide interactive controls for rotation and zoom
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
from molib.core.constants import MoLibConstant
from picogl.backend.gl.api.clear import gl_clear, gl_clear_color
from picogl.backend.gl.api.color import gl_color_material
from picogl.backend.gl.api.enable import (
    gl_disable_capability_list,
    gl_enable_capability_list,
)
from picogl.backend.gl.api.matrix import gl_matrix_mode
from picogl.backend.gl.capability import (
    GLFixedFunctionCapability,
    GLMaterialFace,
    GLPipelineCapability,
)
from picogl.backend.gl.enums import GLBitMask, GLDrawMode
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import (
    gl_load_identity,
    gl_rotatef,
    gl_scalef,
    gl_translate_f,
    gl_viewport,
)
from picogl.backend.gl.lighting.light import LightSource
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import (
    GLCapability,
    GLColorMaterialMode,
    GLFillMode,
    GLLight,
)
from picogl.backend.glu.perspective import glu_perspective
from picogl.core.polygon.mode import gl_polygon_mode
from picogl.core.rgbcolor import RGBAColor, RGBColor
from picogl.core.vec4 import Vec4
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.meshdata import MeshData
from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow
from PySide6.QtCore import Qt, QTimer
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

_EXAMPLES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, _EXAMPLES_DIR)

from utils.pdb_loader import PDBLoader  # noqa: E402

_CHAIN_RGB = {
    "A": RGBColor.GREEN.to_tuple(),
    "B": RGBColor.BLUE.to_tuple(),
}

_VIEWER_LIGHT = LightSource(
    position=Vec4(1.0, 1.0, 1.0, 0.0),
    ambient=RGBAColor(0.4, 0.4, 0.4, 1.0),
    diffuse=RGBAColor(0.6, 0.6, 0.6, 1.0),
    specular=RGBAColor(0.2, 0.2, 0.2, 1.0),
)

_VIEWER_MATERIAL = PhongMaterial(
    ambient=RGBAColor(0.3, 0.3, 0.3, 1.0),
    diffuse=RGBAColor(0.7, 0.7, 0.7, 1.0),
    specular=RGBAColor(0.1, 0.1, 0.1, 1.0),
    shininess=10.0,
)

_LIGHTING_CAPS = [
    GLFixedFunctionCapability.LIGHTING,
    GLFixedFunctionCapability.LIGHT0,
    GLCapability.COLOR_MATERIAL,
]


def _chain_rgb(chain_id: str) -> tuple[float, float, float]:
    return _CHAIN_RGB.get(chain_id, RGBColor.WHITE.to_tuple())


class QtLegacyGLMeshMolecularViewer(QOpenGLWidget):
    """Qt OpenGL widget for displaying molecular structures using LegacyGLMesh."""

    def __init__(self, pdb_path: str, parent=None):
        super().__init__(parent)
        self._initialized = False
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.calpha_atoms = []
        self.calpha_positions = None
        self.calpha_bonds = []

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 1.0
        self.translation_x = 0.0
        self.translation_y = 0.0

        self.last_mouse_pos = None
        self.mouse_pressed = False

        self.wireframe_mode = False
        self.lighting_enabled = False

        self.atoms_mesh = None
        self.bonds_mesh = None

        self._load_pdb_structure()

    def initializeGL(self):
        """Initialize OpenGL settings via PicoGL wrappers."""
        gl_enable_capability_list(
            [
                GLPipelineCapability.DEPTH_TEST,
                *_LIGHTING_CAPS,
            ]
        )
        gl_color_material(
            GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
        )
        gl_clear_color((0.0, 0.0, 0.0, 1.0))

        self._create_mesh_data()
        self._initialized = True
        QTimer.singleShot(100, self._enable_controls)

    def resizeGL(self, width, height):
        """Handle window resize."""
        gl_viewport(0, 0, width, height)
        gl_matrix_mode(GLLegacyMatrixMode.PROJECTION)
        gl_load_identity()
        glu_perspective(45.0, width / max(height, 1), 0.1, 100.0)
        gl_matrix_mode(GLLegacyMatrixMode.MODELVIEW)

    def paintGL(self):
        """Main rendering function."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        gl_load_identity()
        self._apply_lighting()

        gl_translate_f(self.translation_x, self.translation_y, -5.0)
        gl_rotatef(self.rotation_x, 1.0, 0.0, 0.0)
        gl_rotatef(self.rotation_y, 0.0, 1.0, 0.0)
        gl_scalef(self.zoom, self.zoom, self.zoom)

        self._render_molecular_structure()

    def _apply_lighting(self) -> None:
        """Enable or disable fixed-function lighting for this frame."""
        if self.lighting_enabled:
            gl_enable_capability_list(_LIGHTING_CAPS)
            gl_color_material(
                GLMaterialFace.FRONT_AND_BACK, GLColorMaterialMode.AMBIENT_AND_DIFFUSE
            )
            _VIEWER_LIGHT.apply(GLLight.LIGHT0)
            _VIEWER_MATERIAL.apply(GLMaterialFace.FRONT_AND_BACK)
            return
        gl_disable_capability_list(_LIGHTING_CAPS)

    def _load_pdb_structure(self):
        """Load PDB structure and extract C-alpha atoms."""
        print(f"Loading PDB structure from: {self.pdb_path}")

        try:
            self.pdb_loader = PDBLoader(self.pdb_path)
            structure = self.pdb_loader.structure

            print(f"✓ Found {len(structure.atoms)} total atoms")
            print(f"✓ Structure: {structure.title}")
            print(f"✓ Chains: {structure.chains}")
            print(f"✓ Residues: {len(structure.residues)}")

            self.calpha_atoms = [
                atom
                for atom in structure.atoms
                if atom.name == MoLibConstant.PEPTIDE_CHAIN_ATOMNAME
            ]
            print(f"✓ Found {len(self.calpha_atoms)} C-alpha atoms")

            self.calpha_bonds = self._generate_calpha_bonds()
            print(f"✓ Generated {len(self.calpha_bonds)} C-alpha bonds")

        except Exception as e:
            print(f"Error loading PDB file: {e}")
            QMessageBox.critical(None, "Error", f"Failed to load PDB file: {e}")

    def _generate_calpha_bonds(self):
        """Generate bonds between consecutive C-alpha atoms in the same chain."""
        bonds = []
        chain_atoms = {}
        for atom in self.calpha_atoms:
            chain_atoms.setdefault(atom.chain_id, []).append(atom)

        for atoms in chain_atoms.values():
            atoms.sort(key=lambda a: a.res_seq)
            for i in range(len(atoms) - 1):
                bonds.append((atoms[i], atoms[i + 1]))
        return bonds

    def _create_mesh_data(self):
        """Create MeshData for atoms and bonds using PicoGL."""
        if self._initialized:
            return
        atom_vertices, atom_normals, atom_colors_rgba, atom_indices = (
            self._create_sphere_mesh_data()
        )
        bond_vertices, bond_colors, bond_indices = self._create_bond_mesh_data()

        if atom_vertices is not None and len(atom_vertices) > 0:
            mesh_data = MeshData.from_raw(
                vertices=atom_vertices,
                indices=atom_indices,
                colors=atom_colors_rgba[:, :3],
                normals=atom_normals,
            )
            self.atoms_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
            self.atoms_mesh.upload()

        if bond_vertices is not None and len(bond_vertices) > 0:
            self.bonds_mesh = LegacyGLMesh(
                vertices=bond_vertices,
                faces=bond_indices,
                colors=bond_colors[:, :3],
            )
            self.bonds_mesh.upload()

    def _create_sphere_mesh_data(self, radius=0.2, slices=16, stacks=16):
        """Create sphere mesh data for C-alpha atoms."""
        vertices = []
        normals = []
        indices = []

        for i in range(stacks + 1):
            lat = math.pi * (-0.5 + i / stacks)
            z = radius * math.sin(lat)
            zr = radius * math.cos(lat)

            for j in range(slices + 1):
                lng = 2 * math.pi * j / slices
                x = math.cos(lng) * zr
                y = math.sin(lng) * zr
                vertices.append([x, y, z])
                normals.append([x / radius, y / radius, z / radius])

        for i in range(stacks):
            for j in range(slices):
                v1 = i * (slices + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (slices + 1) + j
                v4 = v3 + 1
                indices.extend([v1, v2, v3])
                indices.extend([v2, v4, v3])

        atom_vertices = []
        atom_normals = []
        atom_colors = []
        atom_indices = []
        vertex_offset = 0

        for atom in self.calpha_atoms:
            color = (*_chain_rgb(atom.chain_id), 1.0)
            for vertex in vertices:
                atom_vertices.append(
                    [vertex[0] + atom.x, vertex[1] + atom.y, vertex[2] + atom.z]
                )
                atom_colors.append(color)
            atom_normals.extend(normals)
            for idx in indices:
                atom_indices.append(idx + vertex_offset)
            vertex_offset += len(vertices)

        return (
            np.array(atom_vertices, dtype=np.float32),
            np.array(atom_normals, dtype=np.float32),
            np.array(atom_colors, dtype=np.float32),
            np.array(atom_indices, dtype=np.uint32),
        )

    def _create_bond_mesh_data(self):
        """Create line mesh data for C-alpha bonds."""
        vertices = []
        colors = []
        indices = []

        for atom1, atom2 in self.calpha_bonds:
            color = (*_chain_rgb(atom1.chain_id), 1.0)
            start_idx = len(vertices)
            vertices.append([atom1.x, atom1.y, atom1.z])
            vertices.append([atom2.x, atom2.y, atom2.z])
            colors.extend([color, color])
            indices.extend([start_idx, start_idx + 1])

        return (
            np.array(vertices, dtype=np.float32),
            np.array(colors, dtype=np.float32),
            np.array(indices, dtype=np.uint32),
        )

    def _render_molecular_structure(self):
        """Render the molecular structure using LegacyGLMesh."""
        if self.atoms_mesh is None and self.bonds_mesh is None:
            return

        if self.wireframe_mode:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        else:
            gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.FILL)

        if self.atoms_mesh is not None:
            self.atoms_mesh.draw()

        gl_polygon_mode(GLMaterialFace.FRONT_AND_BACK, GLFillMode.LINE)
        if self.bonds_mesh is not None:
            self.bonds_mesh.draw(GLDrawMode.LINES)

    def _enable_controls(self):
        """Enable control buttons by finding the main window."""
        widget = self.parent()
        while widget is not None:
            if hasattr(widget, "lighting_button"):
                widget.lighting_button.setEnabled(True)
                print("Controls enabled")
                break
            widget = widget.parent()

    def mousePressEvent(self, event):
        """Handle mouse press for rotation."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for rotation."""
        if self.mouse_pressed and self.last_mouse_pos:
            current_pos = event.position().toPoint()
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.last_mouse_pos = current_pos
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.zoom *= zoom_factor
        self.zoom = max(0.01, min(30.0, self.zoom))
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input."""
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
            self.update()
        elif (
            event.key() == Qt.Key_L
            or event.text().lower() == "l"
            or event.key() == Qt.Key_T
            or event.text().lower() == "t"
        ):
            self.lighting_enabled = not self.lighting_enabled
            print(f"Lighting: {'ON' if self.lighting_enabled else 'OFF'}")
            self.update()
        elif event.key() == Qt.Key_Escape:
            self.close()


class LegacyGLMeshMolecularViewerWindow(LegacyQtObjectWindow):
    """Main window for the LegacyGLMesh molecular viewer."""

    def __init__(self, object_file_path: str = None):
        self._pdb_path = object_file_path
        super().__init__(parent=None)
        self.object_file_path = object_file_path

    def ui_init(self):
        """Override ui_init to delay layout creation until we have the PDB path."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.set_layout(self.layout)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(
            "Qt Legacy GLMesh Molecular Viewer - 2VUG C-alpha (Chain A: Green, Chain B: Blue)"
        )
        self.setGeometry(100, 100, 1200, 800)

    def set_layout(self, layout):
        """Build the window layout and GL widget."""
        info_label = QLabel(
            "PDB Structure - C-alpha Atoms (Chain A: Green, Chain B: Blue)"
        )
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")

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

        pdb_path = getattr(self, "_pdb_path", None) or self.object_file_path
        self.gl_widget = QtLegacyGLMeshMolecularViewer(pdb_path)
        lower_layout.addWidget(self.gl_widget)

        controls_layout = QHBoxLayout()
        reset_button = QPushButton("Reset View (R)")
        reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(reset_button)

        info_button = QPushButton("Show Info")
        info_button.clicked.connect(self.show_info)
        controls_layout.addWidget(info_button)

        self.lighting_button = QPushButton("Lighting: OFF")
        self.lighting_button.clicked.connect(self.toggle_lighting)
        self.lighting_button.setEnabled(False)
        controls_layout.addWidget(self.lighting_button)

        controls_layout.addStretch()
        upper_layout.addLayout(controls_layout)

        instructions = QLabel(
            "Controls:\n"
            "• Left mouse: Rotate\n"
            "• Mouse wheel: Zoom\n"
            "• R key: Reset view\n"
            "• W key: Toggle wireframe/filled\n"
            "• L/T key: Toggle lighting\n"
            "• ESC: Exit\n"
            "• Chain A: Green, Chain B: Blue\n"
            "• Using LegacyGLMesh for rendering"
        )
        instructions.setStyleSheet(
            "color: black; font-size: 12px; padding: 10px; background-color: #f0f0f0;"
        )
        upper_layout.addWidget(instructions)

    def reset_view(self):
        """Reset the view to default."""
        if self.gl_widget is None:
            print("OpenGL widget not yet initialized")
            return
        self.gl_widget.rotation_x = 0.0
        self.gl_widget.rotation_y = 0.0
        self.gl_widget.zoom = 1.0
        self.gl_widget.translation_x = 0.0
        self.gl_widget.translation_y = 0.0
        self.gl_widget.update()

    def toggle_lighting(self):
        """Toggle lighting on/off."""
        if self.gl_widget is None:
            print("OpenGL widget not yet initialized")
            return
        self.gl_widget.lighting_enabled = not self.gl_widget.lighting_enabled
        status = "ON" if self.gl_widget.lighting_enabled else "OFF"
        print(f"Lighting: {status}")
        self.lighting_button.setText(f"Lighting: {status}")
        self.gl_widget.update()

    def enable_controls(self):
        """Enable control buttons once OpenGL widget is ready."""
        if hasattr(self, "lighting_button"):
            self.lighting_button.setEnabled(True)
            print("Controls enabled")

    def show_info(self):
        """Show structure information."""
        if self.gl_widget.pdb_loader:
            structure = self.gl_widget.pdb_loader.structure
            info_text = f"""
Structure Information:
Title: {structure.title}
Total atoms: {len(structure.atoms)}
C-alpha atoms: {len(self.gl_widget.calpha_atoms)}
Chains: {structure.chains}
Residues: {len(structure.residues)}
C-alpha bonds: {len(self.gl_widget.calpha_bonds)}

Rendering:
Mode: {'Wireframe' if self.gl_widget.wireframe_mode else 'Filled'}
Using: LegacyGLMesh
            """
            QMessageBox.information(self, "Structure Information", info_text)
        else:
            QMessageBox.warning(self, "No Data", "No PDB structure loaded.")


def main():
    """Main function to run the molecular viewer."""
    app = QApplication(sys.argv)
    pdb_path = os.path.join(_EXAMPLES_DIR, "data", "2VUG.pdb")
    pdb_path = os.path.abspath(pdb_path)
    print(pdb_path)

    if not os.path.exists(pdb_path):
        print(f"Error: PDB file not found at {pdb_path}")
        return 1

    window = LegacyGLMeshMolecularViewerWindow(object_file_path=pdb_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
