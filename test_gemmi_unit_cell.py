#!/usr/bin/env python3
"""
Test script for Gemmi-based unit cell coordinate generation.

This script demonstrates how to use Gemmi to generate crystallographically
accurate unit cell coordinates and axes.
"""

import numpy as np
from picogl.backend.legacy.gizmos.axes.unit_cell_coords import UnitCellCoordinateGenerator

def test_unit_cell_generation():
    """Test the unit cell coordinate generator with different unit cells."""
    
    # Test case 1: Orthorhombic unit cell (P 2 2 2)
    print("=== Test 1: Orthorhombic Unit Cell (P 2 2 2) ===")
    orthorhombic_cell = {
        'a': 50.0,
        'b': 60.0,
        'c': 70.0,
        'alpha': 90.0,
        'beta': 90.0,
        'gamma': 90.0,
        'space_group': 'P 2 2 2'
    }
    
    generator = UnitCellCoordinateGenerator()
    if generator.set_unit_cell(orthorhombic_cell):
        print("✅ Orthorhombic unit cell set successfully")
        
        # Get unit cell information
        info = generator.get_unit_cell_info()
        if info:
            print(f"📦 Unit cell volume: {info['volume']:.1f} Å³")
        
        # Generate axes coordinates
        axes_result = generator.generate_axes_coordinates(axis_length=50.0)
        if axes_result:
            vertices, colors = axes_result
            print(f"✅ Generated axes: {len(vertices)} vertices, {len(colors)} colors")
            print(f"📐 A-axis endpoint: [{vertices[1][0]:.2f}, {vertices[1][1]:.2f}, {vertices[1][2]:.2f}]")
            print(f"📐 B-axis endpoint: [{vertices[3][0]:.2f}, {vertices[3][1]:.2f}, {vertices[3][2]:.2f}]")
            print(f"📐 C-axis endpoint: [{vertices[5][0]:.2f}, {vertices[5][1]:.2f}, {vertices[5][2]:.2f}]")
        
        # Generate unit cell corners
        corners = generator.generate_unit_cell_corners()
        if corners is not None:
            print(f"✅ Generated {len(corners)} unit cell corners")
            print(f"📐 Origin: [{corners[0][0]:.2f}, {corners[0][1]:.2f}, {corners[0][2]:.2f}]")
            print(f"📐 A-corner: [{corners[1][0]:.2f}, {corners[1][1]:.2f}, {corners[1][2]:.2f}]")
            print(f"📐 B-corner: [{corners[2][0]:.2f}, {corners[2][1]:.2f}, {corners[2][2]:.2f}]")
            print(f"📐 C-corner: [{corners[3][0]:.2f}, {corners[3][1]:.2f}, {corners[3][2]:.2f}]")
    else:
        print("❌ Failed to set orthorhombic unit cell")
    
    print("\n" + "="*60 + "\n")
    
    # Test case 2: Monoclinic unit cell (P 2)
    print("=== Test 2: Monoclinic Unit Cell (P 2) ===")
    monoclinic_cell = {
        'a': 45.0,
        'b': 55.0,
        'c': 65.0,
        'alpha': 90.0,
        'beta': 110.0,  # Non-90 degree angle
        'gamma': 90.0,
        'space_group': 'P 2'
    }
    
    generator2 = UnitCellCoordinateGenerator()
    if generator2.set_unit_cell(monoclinic_cell):
        print("✅ Monoclinic unit cell set successfully")
        
        # Get unit cell information
        info = generator2.get_unit_cell_info()
        if info:
            print(f"📦 Unit cell volume: {info['volume']:.1f} Å³")
        
        # Generate axes coordinates
        axes_result = generator2.generate_axes_coordinates(axis_length=50.0)
        if axes_result:
            vertices, colors = axes_result
            print(f"✅ Generated axes: {len(vertices)} vertices, {len(colors)} colors")
            print(f"📐 A-axis endpoint: [{vertices[1][0]:.2f}, {vertices[1][1]:.2f}, {vertices[1][2]:.2f}]")
            print(f"📐 B-axis endpoint: [{vertices[3][0]:.2f}, {vertices[3][1]:.2f}, {vertices[3][2]:.2f}]")
            print(f"📐 C-axis endpoint: [{vertices[5][0]:.2f}, {vertices[5][1]:.2f}, {vertices[5][2]:.2f}]")
            
            # Show how the non-90 degree angle affects the C-axis
            print(f"📐 C-axis is tilted due to β = {monoclinic_cell['beta']}°")
    else:
        print("❌ Failed to set monoclinic unit cell")
    
    print("\n" + "="*60 + "\n")
    
    # Test case 3: Triclinic unit cell (P 1)
    print("=== Test 3: Triclinic Unit Cell (P 1) ===")
    triclinic_cell = {
        'a': 40.0,
        'b': 50.0,
        'c': 60.0,
        'alpha': 85.0,   # Non-90 degree angles
        'beta': 95.0,
        'gamma': 105.0,
        'space_group': 'P 1'
    }
    
    generator3 = UnitCellCoordinateGenerator()
    if generator3.set_unit_cell(triclinic_cell):
        print("✅ Triclinic unit cell set successfully")
        
        # Get unit cell information
        info = generator3.get_unit_cell_info()
        if info:
            print(f"📦 Unit cell volume: {info['volume']:.1f} Å³")
        
        # Generate axes coordinates
        axes_result = generator3.generate_axes_coordinates(axis_length=50.0)
        if axes_result:
            vertices, colors = axes_result
            print(f"✅ Generated axes: {len(vertices)} vertices, {len(colors)} colors")
            print(f"📐 A-axis endpoint: [{vertices[1][0]:.2f}, {vertices[1][1]:.2f}, {vertices[1][2]:.2f}]")
            print(f"📐 B-axis endpoint: [{vertices[3][0]:.2f}, {vertices[3][1]:.2f}, {vertices[3][2]:.2f}]")
            print(f"📐 C-axis endpoint: [{vertices[5][0]:.2f}, {vertices[5][1]:.2f}, {vertices[5][2]:.2f}]")
            
            # Show how all non-90 degree angles affect the axes
            print(f"📐 All axes are tilted due to α = {triclinic_cell['alpha']}°, β = {triclinic_cell['beta']}°, γ = {triclinic_cell['gamma']}°")
    else:
        print("❌ Failed to set triclinic unit cell")

def test_unit_cell_wireframe():
    """Test unit cell wireframe generation."""
    print("\n=== Test 4: Unit Cell Wireframe Generation ===")
    
    # Use a simple orthorhombic cell
    cell_info = {
        'a': 30.0,
        'b': 40.0,
        'c': 50.0,
        'alpha': 90.0,
        'beta': 90.0,
        'gamma': 90.0,
        'space_group': 'P 1'
    }
    
    generator = UnitCellCoordinateGenerator()
    if generator.set_unit_cell(cell_info):
        print("✅ Unit cell set for wireframe generation")
        
        # Generate wireframe
        wireframe_result = generator.generate_unit_cell_edges()
        if wireframe_result:
            corners, edges = wireframe_result
            print(f"✅ Generated wireframe: {len(corners)} corners, {len(edges)} edges")
            
            # Show some edge information
            for i, edge in enumerate(edges[:3]):  # Show first 3 edges
                start, end = edge
                start_pos = corners[start]
                end_pos = corners[end]
                length = np.linalg.norm(end_pos - start_pos)
                print(f"📐 Edge {i+1}: {start}→{end}, length = {length:.2f} Å")
        else:
            print("❌ Failed to generate wireframe")
    else:
        print("❌ Failed to set unit cell for wireframe")

if __name__ == "__main__":
    print("🧪 Testing Gemmi-based Unit Cell Coordinate Generation")
    print("=" * 60)
    
    try:
        test_unit_cell_generation()
        test_unit_cell_wireframe()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
