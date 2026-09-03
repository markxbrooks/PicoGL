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

import os
import sys
from pathlib import Path

from picogl.backend.gl.api.legacy.matrix import gl_matrix_mode_context
from picogl.core.viewport import GLViewport
from picogl.examples.legacy_qt_molecular_viewer import create_molecule_viewer_layout
from molib.core.constants import MoLibConstant
from picogl.backend.gl.api.clear import gl_clear, gl_clear_rgba_color
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
from picogl.backend.gl.enums import GLBitMask
from picogl.backend.gl.enums.legacy import GLLegacyMatrixMode
from picogl.backend.gl.enums.legacy.scale import (
    gl_load_identity,
    gl_viewport,
)
from picogl.backend.gl.lighting.light import LightSource
from picogl.backend.gl.phong.material import PhongMaterial
from picogl.backend.gl.state.fill import (
    GLCapability,
    GLColorMaterialMode,
    GLLight,
)
from picogl.backend.glu.perspective import glu_perspective
from picogl.core.polygon.mode import gl_set_line_mode, gl_set_polygon_mode
from picogl.core.rgbcolor import RGBAColor
from picogl.core.vec4 import Vec4
from picogl.renderer.molecular import AtomsMesh, BondsMesh, chain_rgb
from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from picoui.dimensions import WindowGeometry, Point, Dimensions
from picoui.helpers import create_layout_with_items
from picogl.ui.backend.qt.base import GLTranslation, GLRotation, GLZoom
from picoui.specs.widgets import ButtonSpec
from picoui.widget.helper import create_button_from_spec

DEFAULT_FAR = 100.0

DEFAULT_NEAR = 0.1

DEFAULT_FOVY = 45.0

_EXAMPLES_PATH = Path(__file__).resolve().parent.parent
_EXAMPLES_DIR = str(_EXAMPLES_PATH)
if _EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, _EXAMPLES_DIR)

from picogl.examples.utils.pdb_loader import PDBLoader  # noqa: E402

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
    shininess=50.0,
)

_LIGHTING_CAPS = [
    GLFixedFunctionCapability.LIGHTING,
    GLFixedFunctionCapability.LIGHT0,
    GLCapability.COLOR_MATERIAL,
]


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

        self.last_mouse_pos = None
        self.mouse_pressed = False

        self.wireframe_mode = False
        self.lighting_enabled = False

        self.atoms_mesh = None
        self.bonds_mesh = None

        # Set up view

        self.rotation = GLRotation()
        self.translation = GLTranslation()
        self.viewport = GLViewport(0, 0, self.width(), self.height())
        self._zoom = GLZoom(value=1.0)
        # self._zoom = GLZoom(value=1.0, translation=self.translation)

        self._load_pdb_structure()

    @property
    def zoom(self):
        return self._zoom.value

    @zoom.setter
    def zoom(self, value):
        self._zoom.value = value
        self.update()

    @property
    def rotation_x(self):
        return self.rotation.x

    @rotation_x.setter
    def rotation_x(self, value):
        self.rotation.x = value
        self.rotation.apply()
        self.update()

    @property
    def rotation_y(self):
        return self.rotation.y

    @rotation_y.setter
    def rotation_y(self, value):
        self.rotation.y = value
        self.rotation.apply()
        self.update()

    @property
    def translation_x(self):
        return self.translation.x

    @translation_x.setter
    def translation_x(self, value):
        self.translation.x = value
        self.translation.apply()
        self.update()

    @property
    def translation_y(self):
        return self.translation.y

    @translation_y.setter
    def translation_y(self, value):
        self.translation.y = value
        self.update()


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
        gl_clear_rgba_color(RGBAColor.BLACK)

        self._create_mesh_data()
        self._initialized = True
        QTimer.singleShot(100, self._enable_controls)

    def resizeGL(self, width, height):
        """Handle window resize."""
        self.viewport.update(0, 0, width, height)
        with gl_matrix_mode_context():
            glu_perspective(DEFAULT_FOVY, width / max(height, 1), DEFAULT_NEAR, DEFAULT_FAR)

    def paintGL(self):
        """Main rendering function."""
        gl_clear(GLBitMask.COLOR_BUFFER | GLBitMask.DEPTH_BUFFER)
        gl_load_identity()
        self._apply_lighting()

        self._apply_zoom(self.translation, value=-5.0)
        self._apply_rotation()
        self.rescale()

        self._render_molecular_structure()

    def _apply_rotation(self):
        self.rotation.apply()

    def _apply_zoom(self, translation, value: float = 0.01):
        self._zoom.apply_translation_and_zoom(translation, value)

    def rescale(self):
        self._zoom.rescale()

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
        """Create molecular meshes and upload legacy GPU buffers."""
        if self._initialized:
            return

        if self.calpha_atoms:
            self.atoms_mesh = AtomsMesh(self.calpha_atoms, color_fn=chain_rgb)
            self.atoms_mesh.to_legacy_glmesh(upload=True)

        if self.calpha_bonds:
            self.bonds_mesh = BondsMesh(self.calpha_bonds, color_fn=chain_rgb)
            self.bonds_mesh.to_legacy_glmesh(upload=True)

    def _render_molecular_structure(self):
        """Render the molecular structure using molecular mesh adapters."""
        if self.atoms_mesh is None and self.bonds_mesh is None:
            return

        if self.wireframe_mode:
            gl_set_polygon_mode()
        else:
            gl_set_line_mode()

        if self.atoms_mesh is not None:
            self.atoms_mesh.draw_legacy()

        gl_set_polygon_mode()
        if self.bonds_mesh is not None:
            self.bonds_mesh.draw_legacy()

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
            self.rotation.y += dx * 0.5
            self.rotation.x += dy * 0.5
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
            self.rotation.x = 0.0
            self.rotation.y = 0.0
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

    window_geometry = WindowGeometry(
        position=Point(x=100, y=100),
        dimensions=Dimensions(width=1200, height=800),
    )

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
        self.setGeometry(*window_geometry.to_tuple())

    def set_layout(self, layout):
        """Build the window layout and GL widget."""
        info_label = QLabel(
            "PDB Structure - C-alpha Atoms (Chain A: Green, Chain B: Blue)"
        )
        lower_layout, upper_layout = create_molecule_viewer_layout(info_label, layout)

        pdb_path = getattr(self, "_pdb_path", None) or self.object_file_path
        self.gl_widget = QtLegacyGLMeshMolecularViewer(pdb_path)
        lower_layout.addWidget(self.gl_widget)

        self.specs = self.build_button_specs()

        reset_button = create_button_from_spec(self.specs["reset_button"])
        info_button = create_button_from_spec(self.specs["info_button"])
        self.lighting_button = create_button_from_spec(self.specs["lighting_button"])
        controls_layout_items = [reset_button, info_button, self.lighting_button]
        controls_layout = create_layout_with_items(controls_layout_items,start_stretch=False,  end_stretch=True)

        instructions_label = self.create_instructions_label()

        upper_layout.addLayout(controls_layout)
        upper_layout.addWidget(instructions_label)

    def build_button_specs(self) -> dict[str, ButtonSpec]:
        return {"reset_button": ButtonSpec(label="Reset View (R)", slot=self.reset_view),
        "info_button": ButtonSpec(label="Show Info", slot=self.show_info),
        "lighting_button": ButtonSpec(label="Lighting: OFF", slot=self.toggle_lighting, enabled=False) }

    def create_instructions_label(self) -> QLabel:
        instructions_text = "Controls:\n"
        "• Left mouse: Rotate\n"
        "• Mouse wheel: Zoom\n"
        "• R key: Reset view\n"
        "• W key: Toggle wireframe/filled\n"
        "• L/T key: Toggle lighting\n"
        "• ESC: Exit\n"
        "• Chain A: Green, Chain B: Blue\n"
        "• Using LegacyGLMesh for rendering"
        instructions_style = "color: black; font-size: 12px; padding: 10px; background-color: #f0f0f0;"
        instructions_label = QLabel(instructions_text)
        instructions_label.setStyleSheet(instructions_style)
        return instructions_label

    def reset_view(self):
        """Reset the view to default."""
        if self.gl_widget is None:
            print("OpenGL widget not yet initialized")
            return
        self.gl_widget.rotation.x = 0.0
        self.gl_widget.rotation.y = 0.0
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
    pdb_path = pdb_path = Path(_EXAMPLES_DIR) / "data" / "2VUG.pdb"
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
