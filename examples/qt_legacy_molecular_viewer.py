"""
Qt Legacy Molecular Viewer for PDB Files

This example demonstrates how to:
1. Load PDB files using the PDBLoader
2. Extract C-alpha atoms (CA) from the structure
3. Display them as a white wireframe model using Qt and legacy OpenGL
4. Provide interactive controls for rotation and zoom
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

import numpy as np
from OpenGL.GL import *
from OpenGL.raw.GLU import gluPerspective
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QMessageBox, QSplitter

from examples.utils.pdb_loader import PDBLoader

# Add the examples directory to the path so we can import the PDB loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))



class QtLegacyMolecularViewer(QOpenGLWidget):
    """Qt OpenGL widget for displaying molecular structures with legacy OpenGL"""
    
    def __init__(self, pdb_path: str, parent=None):
        super().__init__(parent)
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
        
        # Load the PDB structure
        self._load_pdb_structure()
        
    def _load_pdb_structure(self):
        """Load PDB structure and extract C-alpha atoms"""
        print(f"Loading PDB structure from: {self.pdb_path}")
        
        try:
            self.pdb_loader = PDBLoader(self.pdb_path)
            structure = self.pdb_loader.structure
            
            # Extract C-alpha atoms (CA)
            self.calpha_atoms = [atom for atom in structure.atoms if atom.name.strip() == "CA"]
            
            print(f"✓ Found {len(self.calpha_atoms)} C-alpha atoms")
            print(f"✓ Structure: {structure.title}")
            print(f"✓ Chains: {structure.chains}")
            
            # Convert to numpy array for rendering
            self.calpha_positions = np.array(
                [[atom.x, atom.y, atom.z] for atom in self.calpha_atoms], 
                dtype=np.float32
            )
            
            # Generate bonds between consecutive C-alpha atoms
            self._generate_calpha_bonds()
            
        except Exception as e:
            print(f"Error loading PDB file: {e}")
            raise
    
    def _generate_calpha_bonds(self):
        """Generate bonds between consecutive C-alpha atoms in the same chain"""
        self.calpha_bonds = []
        
        # Group atoms by chain
        chain_atoms = {}
        for i, atom in enumerate(self.calpha_atoms):
            chain_id = atom.chain_id
            if chain_id not in chain_atoms:
                chain_atoms[chain_id] = []
            chain_atoms[chain_id].append((i, atom))
        
        # Create bonds between consecutive C-alpha atoms in each chain
        for chain_id, atoms in chain_atoms.items():
            # Sort by residue sequence number
            atoms.sort(key=lambda x: x[1].res_seq)
            
            for i in range(len(atoms) - 1):
                idx1, atom1 = atoms[i]
                idx2, atom2 = atoms[i + 1]
                
                # Only create bonds between consecutive residues
                if atom2.res_seq == atom1.res_seq + 1:
                    self.calpha_bonds.append((idx1, idx2))
        
        print(f"✓ Generated {len(self.calpha_bonds)} C-alpha bonds")
    
    def initializeGL(self):
        """Initialize OpenGL state"""
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        
        # Set up lighting for better visibility
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up light
        light_pos = [1.0, 1.0, 1.0, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        ambient = [0.2, 0.2, 0.2, 1.0]
        diffuse = [0.8, 0.8, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    
    def resizeGL(self, width, height):
        """Handle window resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Set up perspective projection
        aspect = width / height if height > 0 else 1.0
        gluPerspective(45.0, aspect, 0.1, 1000.0)
        
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Render the molecular structure"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply camera transformations
        glTranslatef(self.translation_x, self.translation_y, -50.0 * self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Center the structure
        if self.calpha_positions is not None and len(self.calpha_positions) > 0:
            center = np.mean(self.calpha_positions, axis=0)
            glTranslatef(-center[0], -center[1], -center[2])
        
        # Render C-alpha atoms as white wireframe spheres
        self._render_calpha_atoms()
        
        # Render bonds between C-alpha atoms
        self._render_calpha_bonds()
    
    def _render_calpha_atoms(self):
        """Render C-alpha atoms as white wireframe spheres"""
        if self.calpha_positions is None:
            return
        
        glColor3f(1.0, 1.0, 1.0)  # White color
        
        for pos in self.calpha_positions:
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            
            # Draw a small wireframe sphere for each C-alpha atom
            self._draw_wireframe_sphere(0.5, 8, 6)
            
            glPopMatrix()
    
    def _render_calpha_bonds(self):
        """Render bonds between C-alpha atoms as white lines"""
        if not self.calpha_bonds or self.calpha_positions is None:
            return
        
        glColor3f(1.0, 1.0, 1.0)  # White color
        glBegin(GL_LINES)
        
        for atom1_idx, atom2_idx in self.calpha_bonds:
            if 0 <= atom1_idx < len(self.calpha_positions) and 0 <= atom2_idx < len(self.calpha_positions):
                pos1 = self.calpha_positions[atom1_idx]
                pos2 = self.calpha_positions[atom2_idx]
                
                glVertex3f(pos1[0], pos1[1], pos1[2])
                glVertex3f(pos2[0], pos2[1], pos2[2])
        
        glEnd()
    
    def _draw_wireframe_sphere(self, radius, slices, stacks):
        """Draw a wireframe sphere using legacy OpenGL"""
        import math
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + i / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + (i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            glBegin(GL_LINE_LOOP)
            for j in range(slices + 1):
                lng = 2 * math.pi * j / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glVertex3f(x * zr0, y * zr0, z0)
            glEnd()
            
            glBegin(GL_LINES)
            for j in range(slices + 1):
                lng = 2 * math.pi * j / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glVertex3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()
    
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
        self.zoom = max(0.1, min(10.0, self.zoom))  # Clamp zoom
        self.update()
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_R:
            # Reset view
            self.rotation_x = 0.0
            self.rotation_y = 0.0
            self.zoom = 1.0
            self.translation_x = 0.0
            self.translation_y = 0.0
            self.update()
        elif event.key() == Qt.Key_Escape:
            self.close()


class MolecularViewerWindow(QMainWindow):
    """Main window for the molecular viewer"""
    
    def __init__(self, pdb_path: str):
        super().__init__()
        self.gl_widget = None
        self.pdb_path = pdb_path
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Qt Legacy Molecular Viewer - 2VUG C-alpha Wireframe")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add info label
        info_label = QLabel("2VUG PDB Structure - C-alpha Atoms (White Wireframe)")
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
        # Add controls
        controls_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset View (R)")
        reset_button.clicked.connect(self.reset_view)
        controls_layout.addWidget(reset_button)
        
        info_button = QPushButton("Show Info")
        info_button.clicked.connect(self.show_info)
        controls_layout.addWidget(info_button)
        
        controls_layout.addStretch()
        upper_layout.addLayout(controls_layout)
        
        # Create OpenGL widget
        self.gl_widget = QtLegacyMolecularViewer(self.pdb_path)
        lower_layout.addWidget(self.gl_widget)
        
        # Add instructions
        instructions = QLabel(
            "Controls:\n"
            "• Left mouse: Rotate\n"
            "• Mouse wheel: Zoom\n"
            "• R key: Reset view\n"
            "• ESC: Exit"
        )
        instructions.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0;")
        upper_layout.addWidget(instructions)
    
    def reset_view(self):
        """Reset the view to default"""
        self.gl_widget.rotation_x = 0.0
        self.gl_widget.rotation_y = 0.0
        self.gl_widget.zoom = 1.0
        self.gl_widget.translation_x = 0.0
        self.gl_widget.translation_y = 0.0
        self.gl_widget.update()
    
    def show_info(self):
        """Show structure information"""
        if self.gl_widget.pdb_loader:
            structure = self.gl_widget.pdb_loader.structure
            info_text = (
                f"Structure: {structure.title}\n"
                f"C-alpha atoms: {len(self.gl_widget.calpha_atoms)}\n"
                f"C-alpha bonds: {len(self.gl_widget.calpha_bonds)}\n"
                f"Chains: {', '.join(structure.chains)}\n"
                f"Total atoms: {len(structure.atoms)}"
            )
            
            QMessageBox.information(self, "Structure Information", info_text)


def main():
    """Main function to run the molecular viewer"""
    app = QApplication(sys.argv)
    
    # Path to the 2VUG.pdb file
    pdb_path = os.path.join(os.path.dirname(__file__), "data", "2VUG.pdb")
    
    if not os.path.exists(pdb_path):
        print(f"Error: PDB file not found at {pdb_path}")
        print("Please ensure 2VUG.pdb is in the examples/data/ directory")
        return 1
    
    # Create and show the main window
    window = MolecularViewerWindow(pdb_path)
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
