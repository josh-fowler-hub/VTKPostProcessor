#!/usr/bin/env python3
"""
Test script for geometry surface contour visualization

This script demonstrates the new plot_geometry_surface_contours() method 
which shows field values directly on the 3D geometry surfaces, giving you
the actual shape of the CFD geometry with contours on the surfaces.
"""

from PostProcessing.VTKPostProcessor import CFDPostProcessor
import os

def test_geometry_surface_contours():
    """Test the new geometry surface contour functionality"""
    
    # Create processor
    processor = CFDPostProcessor('geom_vol.vtm')
    
    # Get available data
    print("=== Available Data ===")
    block_names = processor.get_block_names()
    print(f"Blocks: {block_names}")
    
    # Show available variables for first block
    if block_names:
        first_block = block_names[0]
        cell_vars, point_vars = processor.get_available_variables(block_name=first_block)
        print(f"\nVariables in '{first_block}':")
        print(f"  Cell data: {cell_vars}")
        print(f"  Point data: {point_vars}")
    
    # Create output directory
    os.makedirs('geometry_surface_tests', exist_ok=True)
    
    print("\n=== Testing Geometry Surface Contours ===")
    
    # Test 1: Single block with cell data
    if block_names and cell_vars:
        print(f"\nTest 1: Single block geometry surface contours")
        try:
            files = processor.plot_geometry_surface_contours(
                field_name=cell_vars[0],  # First available cell variable
                data_type='cell',
                block_name=first_block,
                save_path=f'geometry_surface_tests/test_single_block.html'
            )
            print(f"  ✓ Created: {files}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Test 2: All blocks
    if len(block_names) > 1 and cell_vars:
        print(f"\nTest 2: All blocks geometry surface contours")
        try:
            files = processor.plot_geometry_surface_contours(
                field_name=cell_vars[0],
                data_type='cell',
                block_name=None,  # All blocks
                save_path='geometry_surface_tests/test_all_blocks.html'
            )
            print(f"  ✓ Created: {files}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Test 3: Multiple specific blocks
    if len(block_names) >= 2 and cell_vars:
        print(f"\nTest 3: Multiple specific blocks")
        try:
            files = processor.plot_geometry_surface_contours(
                field_name=cell_vars[0],
                data_type='cell',
                block_name=block_names[:2],  # First two blocks
                save_path='geometry_surface_tests/test_multiple_blocks.html'
            )
            print(f"  ✓ Created: {files}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Test 4: Point data (if available)
    if block_names and point_vars:
        print(f"\nTest 4: Point data geometry surface contours")
        try:
            files = processor.plot_geometry_surface_contours(
                field_name=point_vars[0],  # First available point variable
                data_type='point',
                block_name=first_block,
                save_path=f'geometry_surface_tests/test_point_data.html'
            )
            print(f"  ✓ Created: {files}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print("\n=== Test Complete ===")
    print("Generated files:")
    if os.path.exists('geometry_surface_tests'):
        for file in os.listdir('geometry_surface_tests'):
            if file.endswith('.html'):
                print(f"  - geometry_surface_tests/{file}")
    
    print("\n=== Usage Notes ===")
    print("The geometry surface contour plots show:")
    print("• Actual 3D shape of your CFD geometry")
    print("• Field values (pressure, velocity, etc.) as colors on the surfaces")
    print("• Interactive 3D visualization with rotation, zoom, pan")
    print("• Color scale showing min/max values")
    print("\nThis is different from coordinate projections - you see the real geometry!")

if __name__ == "__main__":
    test_geometry_surface_contours()