#!/usr/bin/env python3
"""
Test script for combined geometry surface contour visualization

This script demonstrates the new plot_geometry_surface_contours_combined() method 
which creates a single plot showing all blocks with contours for one variable.
"""

from VTKPostProcessor import CFDPostProcessor
import os

def test_combined_geometry_surface_contours():
    """Test the new combined geometry surface contour functionality"""
    
    # Create processor
    processor = CFDPostProcessor('geom_vol.vtm')
    
    # Get available data
    print("=== Available Data ===")
    block_names = processor.get_block_names()
    print(f"Blocks: {block_names}")
    
    # Collect all variables across all blocks
    all_variables = set()
    block_variables = {}
    
    for block_name in block_names:
        cell_vars, point_vars = processor.get_available_variables(block_name=block_name)
        block_variables[block_name] = {'cell_data': cell_vars, 'point_data': point_vars}
        all_variables.update(cell_vars)
    
    print(f"\nAll variables found: {sorted(all_variables)}")
    
    # Create output directory
    os.makedirs('combined_geometry_tests', exist_ok=True)
    
    print("\n=== Testing Combined Geometry Surface Contours ===")
    print("This creates ONE plot per variable, combining ALL blocks that have that variable")
    
    # Test: Create combined plots for each variable
    for var_name in sorted(all_variables):
        print(f"\nProcessing variable '{var_name}'...")
        
        # Find which blocks have this variable
        blocks_with_variable = []
        for block_name in block_names:
            if block_name in block_variables:
                cell_vars = block_variables[block_name]['cell_data']
                if var_name in cell_vars:
                    blocks_with_variable.append(block_name)
        
        if blocks_with_variable:
            print(f"  Found '{var_name}' in blocks: {blocks_with_variable}")
            try:
                file_path = processor.plot_geometry_surface_contours_combined(
                    field_name=var_name,
                    block_name=blocks_with_variable,  # List of blocks with this variable
                    data_type='cell',
                    save_path=f'combined_geometry_tests/combined_{var_name}_all_blocks.html'
                )
                print(f"  ✓ Created: {file_path}")
                print(f"    Shows {len(blocks_with_variable)} blocks with '{var_name}' in one plot")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        else:
            print(f"  Skipping '{var_name}' - not found in any blocks")
    
    print("\n=== Test Complete ===")
    print("Generated files:")
    if os.path.exists('combined_geometry_tests'):
        for file in os.listdir('combined_geometry_tests'):
            if file.endswith('.html'):
                print(f"  - combined_geometry_tests/{file}")
    
    print("\n=== What You Get ===")
    print("Each HTML file contains:")
    print("• ONE interactive 3D plot per variable")
    print("• ALL blocks that contain that variable in the same plot")
    print("• Consistent color scale across all blocks")
    print("• Each block shown as a separate mesh in the same scene")
    print("• Legend showing which mesh corresponds to which block")
    print("\nThis lets you see how a single variable (like pressure) varies")
    print("across the entire geometry, with all blocks visible together!")

if __name__ == "__main__":
    test_combined_geometry_surface_contours()