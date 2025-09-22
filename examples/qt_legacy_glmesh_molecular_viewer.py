"""
Qt Legacy GLMesh Molecular Viewer for PDB Files

This example demonstrates how to:
1. Load PDB files using the PDBLoader
2. Extract C-alpha atoms (CA) from the structure
3. Convert them to PicoGL MeshData format
4. Display them using LegacyGLMesh for rendering
5. Provide interactive controls for rotation and zoom
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple
import math

import numpy as np
from OpenGL.GL import *
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_LINES
from OpenGL.raw.GLU import gluPerspective
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QMessageBox, QSplitter

from picogl.ui.backend.qt.legacy.window import LegacyQtObjectWindow
from picogl.renderer.legacy_glmesh import LegacyGLMesh
from picogl.renderer.meshdata import MeshData

# Add the examples directory to the path so we can import the PDB loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from pdb_loader import PDBLoader, Atom


class QtLegacyGLMeshMolecularViewer(QOpenGLWidget):
    """Qt OpenGL widget for displaying molecular structures using LegacyGLMesh"""

    def __init__(self, pdb_path: str, parent=None):
        super().__init__(parent)
        self._initialized = False
        self.pdb_path = pdb_path
        self.pdb_loader = None
        self.calpha_atoms = []
        self.calpha_positions = None
        self.calpha_bonds = []

        # Camera parameters
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = 1.0
        self.translation_x = 0.0
        self.translation_y = 0.0

        # Mouse interaction
        self.last_mouse_pos = None
        self.mouse_pressed = False

        # Rendering mode
        self.wireframe_mode = False
        self.lighting_enabled = False  # Turn off fancy lighting by default

        # PicoGL meshes
        self.atoms_mesh = None
        self.bonds_mesh = None

        # Load the PDB structure (but don't create meshes yet)
        self._load_pdb_structure()

    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glClearColor(0.0, 0.0, 0.0, 1.0)

        # Create meshes now that OpenGL context is ready
        self._create_mesh_data()
        self._initialized = True
        
        # Enable controls after a short delay to ensure everything is ready
        QTimer.singleShot(100, self._enable_controls)

    def resizeGL(self, width, height):
        """Handle window resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Main rendering function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up lighting conditionally
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            # Set up lighting in world space (before transformations)
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])  # Higher ambient for more consistent lighting
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.6, 1.0])  # Reduced diffuse
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])  # Much lower specular

            # Set material properties to be more diffuse and less specular
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])  # Very low specular
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10.0)  # Lower shininess
        else:
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glDisable(GL_COLOR_MATERIAL)

        # Apply transformations
        glTranslatef(self.translation_x, self.translation_y, -5.0)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        glScalef(self.zoom, self.zoom, self.zoom)

        # Render the molecular structure using LegacyGLMesh
        self._render_molecular_structure()

    def _load_pdb_structure(self):
        """Load PDB structure and extract C-alpha atoms"""
        print(f"Loading PDB structure from: {self.pdb_path}")

        try:
            self.pdb_loader = PDBLoader(self.pdb_path)
            structure = self.pdb_loader.structure

            print(f"✓ Found {len(structure.atoms)} total atoms")
            print(f"✓ Structure: {structure.title}")
            print(f"✓ Chains: {structure.chains}")
            print(f"✓ Residues: {len(structure.residues)}")

            # Extract C-alpha atoms
            self.calpha_atoms = [atom for atom in structure.atoms if atom.name == "CA"]
            print(f"✓ Found {len(self.calpha_atoms)} C-alpha atoms")

            # Generate C-alpha bonds (sequential bonds within each chain)
            self.calpha_bonds = self._generate_calpha_bonds()
            print(f"✓ Generated {len(self.calpha_bonds)} C-alpha bonds")

            # Note: Mesh data will be created in initializeGL when OpenGL context is ready

        except Exception as e:
            print(f"Error loading PDB file: {e}")
            QMessageBox.critical(None, "Error", f"Failed to load PDB file: {e}")

    def _generate_calpha_bonds(self):
        """Generate bonds between consecutive C-alpha atoms in the same chain"""
        bonds = []

        # Group atoms by chain
        chain_atoms = {}
        for atom in self.calpha_atoms:
            if atom.chain_id not in chain_atoms:
                chain_atoms[atom.chain_id] = []
            chain_atoms[atom.chain_id].append(atom)

        # Create bonds within each chain
        for chain_id, atoms in chain_atoms.items():
            # Sort atoms by residue number
            atoms.sort(key=lambda a: a.res_seq)

            # Create bonds between consecutive atoms
            for i in range(len(atoms) - 1):
                bonds.append((atoms[i], atoms[i + 1]))

        return bonds

    def _create_mesh_data(self):
        """Create MeshData for atoms and bonds using PicoGL"""
        # Create sphere mesh data for atoms
        if self._initialized:
            return
        atom_vertices, atom_normals, atom_colors_rgba, atom_indices = self._create_sphere_mesh_data()

        # Create line mesh data for bonds
        bond_vertices, bond_colors, bond_indices = self._create_bond_mesh_data()
        # Convert RGBA colors to RGB for LegacyGLMesh
        atom_colors_rgb = atom_colors_rgba[:, :3]  # Remove alpha channel
        mesh_data = MeshData.from_raw(vertices=atom_vertices,
                                      indices=atom_indices,
                                      colors=atom_colors_rgb)

        # Create atoms mesh
        if atom_vertices is not None:
            self.atoms_mesh = LegacyGLMesh.from_mesh_data(mesh_data)
            self.atoms_mesh.upload()

        # Create bonds mesh
        if bond_vertices is not None:
            # Convert RGBA colors to RGB for LegacyGLMesh
            bond_colors_rgb = bond_colors[:, :3]  # Remove alpha channel
            self.bonds_mesh = LegacyGLMesh(
                vertices=bond_vertices,
                faces=bond_indices,
                colors=bond_colors_rgb
            )
            self.bonds_mesh.upload()

    def _create_sphere_mesh_data(self, radius=0.2, slices=16, stacks=16):
        """Create sphere mesh data for C-alpha atoms"""
        vertices = []
        normals = []
        colors = []
        indices = []

        # Generate sphere geometry
        for i in range(stacks + 1):
            lat = math.pi * (-0.5 + i / stacks)
            z = radius * math.sin(lat)
            zr = radius * math.cos(lat)

            for j in range(slices + 1):
                lng = 2 * math.pi * j / slices
                x = math.cos(lng) * zr
                y = math.sin(lng) * zr

                # Calculate normal
                nx = x / radius
                ny = y / radius
                nz = z / radius

                vertices.append([x, y, z])
                normals.append([nx, ny, nz])

        # Generate indices for triangles
        for i in range(stacks):
            for j in range(slices):
                # Current quad
                v1 = i * (slices + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (slices + 1) + j
                v4 = v3 + 1

                # Create two triangles
                indices.extend([v1, v2, v3])
                indices.extend([v2, v4, v3])

        # Create vertices for each atom
        atom_vertices = []
        atom_normals = []
        atom_colors = []
        atom_indices = []

        vertex_offset = 0

        for atom in self.calpha_atoms:
            # Set colour based on chain
            if atom.chain_id == 'A':
                color = [0.0, 1.0, 0.0, 1.0]  # Green
            elif atom.chain_id == 'B':
                color = [0.0, 0.0, 1.0, 1.0]  # Blue
            else:
                color = [1.0, 1.0, 1.0, 1.0]  # White for other chains

            # Add sphere vertices for this atom
            for vertex in vertices:
                atom_vertices.append([
                    vertex[0] + atom.x,
                    vertex[1] + atom.y,
                    vertex[2] + atom.z
                ])
                atom_colors.append(color)

            # Add normals (same for all atoms)
            atom_normals.extend(normals)

            # Add indices for this atom's sphere
            for idx in indices:
                atom_indices.append(idx + vertex_offset)

            vertex_offset += len(vertices)

        return (
            np.array(atom_vertices, dtype=np.float32),
            np.array(atom_normals, dtype=np.float32),
            np.array(atom_colors, dtype=np.float32),
            np.array(atom_indices, dtype=np.uint32)
        )

    def _create_bond_mesh_data(self):
        """Create line mesh data for C-alpha bonds"""
        vertices = []
        colors = []
        indices = []

        for i, (atom1, atom2) in enumerate(self.calpha_bonds):
            # Set colour based on chain
            if atom1.chain_id == 'A':
                color = [0.0, 1.0, 0.0, 1.0]  # Green
            elif atom1.chain_id == 'B':
                color = [0.0, 0.0, 1.0, 1.0]  # Blue
            else:
                color = [1.0, 1.0, 1.0, 1.0]  # White for other chains

            # Add vertices for this bond
            start_idx = len(vertices)
            vertices.append([atom1.x, atom1.y, atom1.z])
            vertices.append([atom2.x, atom2.y, atom2.z])
            colors.extend([color, color])

            # Add indices for this bond
            indices.extend([start_idx, start_idx + 1])

        return (
            np.array(vertices, dtype=np.float32),
            np.array(colors, dtype=np.float32),
            np.array(indices, dtype=np.uint32)
        )

    def _render_molecular_structure(self):
        """Render the molecular structure using LegacyGLMesh"""
        if self.atoms_mesh is None or self.bonds_mesh is None:
            return

        # Set polygon mode based on wireframe mode
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Render atoms
        if self.atoms_mesh:
            self.atoms_mesh.draw()

        # Always render bonds as lines
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        if self.bonds_mesh:
            self.bonds_mesh.draw(GL_LINES)

    def _enable_controls(self):
        """Enable control buttons by finding the main window"""
        # Walk up the widget hierarchy to find the main window
        widget = self.parent()
        while widget is not None:
            if hasattr(widget, 'lighting_button'):
                widget.lighting_button.setEnabled(True)
                print("Controls enabled")
                break
            widget = widget.parent()

    def mousePressEvent(self, event):
        """Handle mouse press for rotation"""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for rotation"""
        if self.mouse_pressed and self.last_mouse_pos:
            current_pos = event.position().toPoint()
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()

            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            self.last_mouse_pos = current_pos
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.zoom *= zoom_factor
        self.zoom = max(0.01, min(30.0, self.zoom))  # Clamp zoom
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        # Debug: print the key that was pressed
        print(f"Key pressed: {event.key()}, Qt.Key_L = {Qt.Key_L}")

        if event.key() == Qt.Key_R:
            # Reset view
            self.rotation_x = 0.0
            self.rotation_y = 0.0
            self.zoom = 1.0
            self.translation_x = 0.0
            self.translation_y = 0.0
            self.update()
        elif event.key() == Qt.Key_W:
            # Toggle wireframe mode
            self.wireframe_mode = not self.wireframe_mode
            print(f"Wireframe mode: {'ON' if self.wireframe_mode else 'OFF'}")
            self.update()
        elif event.key() == Qt.Key_L or event.text().lower() == 'l' or event.key() == Qt.Key_T or event.text().lower() == 't':
            # Toggle lighting
            self.lighting_enabled = not self.lighting_enabled
            print(f"Lighting: {'ON' if self.lighting_enabled else 'OFF'}")
            self.update()
        elif event.key() == Qt.Key_Escape:
            self.close()


class LegacyGLMeshMolecularViewerWindow(LegacyQtObjectWindow):
    """Main window for the LegacyGLMesh molecular viewer"""

    def __init__(self, object_file_path: str = None):
        # Store the object file path before calling parent constructor
        self._pdb_path = object_file_path
        super().__init__(parent=None)
        # Set the object file path after parent constructor (which sets it to None)
        self.object_file_path = object_file_path

    def ui_init(self):
        """Override ui_init to delay layout creation until we have the PDB path"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Create layout
        self.layout = QVBoxLayout(central_widget)
        # Create info label
        self.set_layout(self.layout)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Qt Legacy GLMesh Molecular Viewer - 2VUG C-alpha (Chain A: Green, Chain B: Blue)")
        self.setGeometry(100, 100, 1200, 800)

    def set_layout(self, layout):
        """set layout"""
        # Add info label
        info_label = QLabel("PDB Structure - C-alpha Atoms (Chain A: Green, Chain B: Blue)")
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
        # Create OpenGL widget with the PDB path first
        pdb_path = getattr(self, '_pdb_path', None) or self.object_file_path
        self.gl_widget = QtLegacyGLMeshMolecularViewer(pdb_path)
        lower_layout.addWidget(self.gl_widget)

        # Add controls
        controls_layout = QHBoxLayout()

        reset_button = QPushButton("Reset View (R)")
        reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(reset_button)

        info_button = QPushButton("Show Info")
        info_button.clicked.connect(self.show_info)
        controls_layout.addWidget(info_button)

        self.lighting_button = QPushButton("Lighting: OFF")
        self.lighting_button.clicked.connect(self.toggle_lighting)
        self.lighting_button.setEnabled(False)  # Disable until widget is ready
        controls_layout.addWidget(self.lighting_button)

        controls_layout.addStretch()
        upper_layout.addLayout(controls_layout)

        # Add instructions
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
        instructions.setStyleSheet("colour: black; font-size: 12px; padding: 10px; background-colour: #f0f0f0;")
        upper_layout.addWidget(instructions)

    def reset_view(self):
        """Reset the view to default"""
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
        """Toggle lighting on/off"""
        if self.gl_widget is None:
            print("OpenGL widget not yet initialized")
            return
        
        self.gl_widget.lighting_enabled = not self.gl_widget.lighting_enabled
        status = "ON" if self.gl_widget.lighting_enabled else "OFF"
        print(f"Lighting: {status}")
        self.lighting_button.setText(f"Lighting: {status}")
        self.gl_widget.update()
    
    def enable_controls(self):
        """Enable control buttons once OpenGL widget is ready"""
        if hasattr(self, 'lighting_button'):
            self.lighting_button.setEnabled(True)
            print("Controls enabled")

    def show_info(self):
        """Show structure information"""
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
    """Main function to run the molecular viewer"""
    app = QApplication(sys.argv)

    # Path to the 2VUG.pdb file
    pdb_path = os.path.join(os.path.dirname(__file__), "data", "2VUG.pdb")
    print(pdb_path)
    pdb_path = os.path.abspath(pdb_path)
    print(pdb_path)

    if not os.path.exists(pdb_path):
        print(f"Error: PDB file not found at {pdb_path}")
        return 1

    # Create and show the main window
    window = LegacyGLMeshMolecularViewerWindow(object_file_path=pdb_path)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
