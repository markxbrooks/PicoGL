#!/usr/bin/env python3
"""
Test script for the LegacyGLMesh Molecular Viewer
"""

import os
import sys


def test_imports():
    """Test importing the molecular viewer components"""
    print("🧪 Testing LegacyGLMesh Molecular Viewer Imports")
    print("=" * 50)

    try:
        # Test PDB loader import
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
        from pdb_loader import Atom, PDBLoader

        print("✅ Successfully imported PDBLoader and Atom")

        # Test PicoGL imports
        from picogl.renderer.legacy_glmesh import LegacyGLMesh
        from picogl.renderer.meshdata import MeshData

        print("✅ Successfully imported LegacyGLMesh and MeshData")

        # Test Qt imports
        from PySide6.QtCore import Qt
        from PySide6.QtOpenGLWidgets import QOpenGLWidget
        from PySide6.QtWidgets import QApplication

        print("✅ Successfully imported PySide6 components")

        # Test molecular viewer import
        from legacy_qt_glmesh_molecular_viewer import (
            LegacyGLMeshMolecularViewerWindow,
            QtLegacyGLMeshMolecularViewer,
        )

        print("✅ Successfully imported QtLegacyGLMeshMolecularViewer")
        print("✅ Successfully imported LegacyGLMeshMolecularViewerWindow")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_pdb_loading():
    """Test PDB loading functionality"""
    print("\n🧬 Testing PDB Loading")
    print("=" * 30)

    try:
        # Load PDB file
        pdb_path = os.path.join(os.path.dirname(__file__), "data", "2VUG.pdb")
        pdb_path = os.path.abspath(pdb_path)

        if not os.path.exists(pdb_path):
            print(f"❌ PDB file not found at {pdb_path}")
            return False

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
        from pdb_loader import PDBLoader

        pdb_loader = PDBLoader(pdb_path)
        structure = pdb_loader.structure

        print(f"✅ Loaded PDB structure: {structure.title}")
        print(f"   Total atoms: {len(structure.atoms)}")
        print(f"   Chains: {structure.chains}")
        print(f"   Residues: {len(structure.residues)}")

        # Test C-alpha extraction
        calpha_atoms = [
            atom
            for atom in structure.atoms
            if atom.name == MoLibConstant.PEPTIDE_CHAIN_ATOMNAME
        ]
        print(f"✅ C-alpha atoms: {len(calpha_atoms)}")

        # Test chain distribution
        chain_a_atoms = [atom for atom in calpha_atoms if atom.chain_id == "A"]
        chain_b_atoms = [atom for atom in calpha_atoms if atom.chain_id == "B"]

        print(f"   Chain A: {len(chain_a_atoms)} atoms (Green)")
        print(f"   Chain B: {len(chain_b_atoms)} atoms (Blue)")

        return True

    except Exception as e:
        print(f"❌ Error loading PDB: {e}")
        return False


def test_mesh_data_creation():
    """Test mesh data creation without OpenGL context"""
    print("\n🔧 Testing Mesh Data Creation")
    print("=" * 35)

    try:
        import math

        import numpy as np

        # Create simple sphere data
        radius = 0.2
        slices = 8
        stacks = 8

        vertices = []
        normals = []
        colors = []
        indices = []

        # Generate sphere meshdata
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
                colors.append([1.0, 0.0, 0.0])  # Red

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

        print(
            f"✅ Generated sphere with {len(vertices)} vertices, {len(indices)} indices"
        )

        # Convert to numpy arrays
        vertices_array = np.array(vertices, dtype=np.float32)
        normals_array = np.array(normals, dtype=np.float32)
        colors_array = np.array(colors, dtype=np.float32)
        indices_array = np.array(indices, dtype=np.uint32)

        print(
            f"✅ Arrays created - vertices: {vertices_array.shape}, colors: {colors_array.shape}"
        )

        # Test bond data creation
        bond_vertices = [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
        ]

        bond_colors = [
            [1.0, 0.0, 0.0],  # Red
            [1.0, 0.0, 0.0],  # Red
            [0.0, 1.0, 0.0],  # Green
            [0.0, 1.0, 0.0],  # Green
        ]

        bond_indices = [0, 1, 2, 3]  # Two lines

        bond_vertices_array = np.array(bond_vertices, dtype=np.float32)
        bond_colors_array = np.array(bond_colors, dtype=np.float32)
        bond_indices_array = np.array(bond_indices, dtype=np.uint32)

        print(
            f"✅ Bond data created - vertices: {bond_vertices_array.shape}, colors: {bond_colors_array.shape}"
        )

        return True

    except Exception as e:
        print(f"❌ Error creating mesh data: {e}")
        return False


def main():
    """Main test function"""
    print("🧬 LegacyGLMesh Molecular Viewer Test Suite")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("PDB Loading Test", test_pdb_loading),
        ("Mesh Data Creation Test", test_mesh_data_creation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            print(f"✅ {test_name} - PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} - FAILED")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The LegacyGLMesh molecular viewer is ready to use.")
        print("\n🚀 To run the molecular viewer:")
        print("   python legacy_qt_glmesh_molecular_viewer.py")
        print("")
        print("🎮 Controls:")
        print("   • Left mouse: Rotate")
        print("   • Mouse wheel: Zoom")
        print("   • R key: Reset view")
        print("   • W key: Toggle wireframe/filled spheres")
        print("   • ESC: Exit")
        print("")
        print("🔧 Features:")
        print("   • Uses LegacyGLMesh for rendering")
        print("   • Chain A: Green, Chain B: Blue")
        print("   • C-alpha atoms as spheres")
        print("   • C-alpha bonds as lines")
        print("   • Wireframe/filled toggle")
    else:
        print("⚠️  Some tests failed. Please check the error above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
