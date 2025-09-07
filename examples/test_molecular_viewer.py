"""
Test script for Qt Legacy Molecular Viewer

This script tests the molecular viewer functionality without requiring a display.
"""

import sys
import os
from pathlib import Path

# Add the examples directory to the path so we can import the PDB loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from pdb_loader import PDBLoader


def test_pdb_loading():
    """Test PDB loading and C-alpha extraction"""
    print("🧬 Testing PDB Loading and C-alpha Extraction")
    print("=" * 50)
    
    # Path to the 2VUG.pdb file
    pdb_path = os.path.join(os.path.dirname(__file__), "data", "2VUG.pdb")
    
    if not os.path.exists(pdb_path):
        print(f"❌ Error: PDB file not found at {pdb_path}")
        return False
    
    try:
        # Load PDB structure
        print(f"📁 Loading PDB file: {pdb_path}")
        pdb_loader = PDBLoader(pdb_path)
        structure = pdb_loader.structure
        
        print(f"✅ Successfully loaded PDB structure")
        print(f"   Title: {structure.title}")
        print(f"   Total atoms: {len(structure.atoms)}")
        print(f"   Total bonds: {len(structure.bonds)}")
        print(f"   Chains: {structure.chains}")
        print(f"   Residues: {len(structure.residues)}")
        
        # Extract C-alpha atoms
        calpha_atoms = [atom for atom in structure.atoms if atom.name.strip() == "CA"]
        print(f"\n🔬 C-alpha Analysis:")
        print(f"   C-alpha atoms found: {len(calpha_atoms)}")
        
        if calpha_atoms:
            # Group by chain
            chain_counts = {}
            for atom in calpha_atoms:
                chain_id = atom.chain_id
                chain_counts[chain_id] = chain_counts.get(chain_id, 0) + 1
            
            print(f"   C-alpha atoms per chain:")
            for chain_id, count in chain_counts.items():
                print(f"     Chain {chain_id}: {count} atoms")
            
            # Show first few C-alpha atoms
            print(f"\n📍 First 5 C-alpha atoms:")
            for i, atom in enumerate(calpha_atoms[:5]):
                print(f"   {i+1}. Chain {atom.chain_id}, Residue {atom.res_seq} ({atom.res_name}): "
                      f"({atom.x:.2f}, {atom.y:.2f}, {atom.z:.2f})")
        
        # Test bond generation
        print(f"\n🔗 Bond Analysis:")
        calpha_bonds = []
        
        # Group atoms by chain
        chain_atoms = {}
        for i, atom in enumerate(calpha_atoms):
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
                    calpha_bonds.append((idx1, idx2))
        
        print(f"   C-alpha bonds generated: {len(calpha_bonds)}")
        
        # Show bond statistics per chain
        chain_bonds = {}
        for bond in calpha_bonds:
            atom1 = calpha_atoms[bond[0]]
            chain_id = atom1.chain_id
            chain_bonds[chain_id] = chain_bonds.get(chain_id, 0) + 1
        
        print(f"   C-alpha bonds per chain:")
        for chain_id, count in chain_bonds.items():
            print(f"     Chain {chain_id}: {count} bonds")
        
        print(f"\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_molecular_viewer_import():
    """Test that the molecular viewer can be imported"""
    print("\n🔧 Testing Molecular Viewer Import")
    print("=" * 50)
    
    try:
        # Try to import the molecular viewer
        from qt_legacy_molecular_viewer import QtLegacyMolecularViewer, MolecularViewerWindow
        print("✅ Successfully imported QtLegacyMolecularViewer")
        print("✅ Successfully imported MolecularViewerWindow")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧬 Qt Legacy Molecular Viewer Test Suite")
    print("=" * 60)
    
    tests = [
        ("PDB Loading and C-alpha Extraction", test_pdb_loading),
        ("Molecular Viewer Import", test_molecular_viewer_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The molecular viewer is ready to use.")
        print("\n🚀 To run the molecular viewer:")
        print("   python qt_legacy_molecular_viewer.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
