#!/usr/bin/env python3
"""
Test script demonstrating flexible block specification API
"""

from VTKPostProcessor import VTKPostProcessor

def test_flexible_blocks():
    """Test the new flexible block specification API"""
    
    # Initialize processor - adjust path to your VTU file
    vtk_file = 'path_to_your.vtu'  # Replace with actual path
    processor = VTKPostProcessor(vtk_file)
    
    print("\n" + "="*60)
    print("Testing Flexible Block Specification API")
    print("="*60)
    
    # Show available blocks
    print(f"\nAvailable blocks: {processor.block_names}")
    
    # Example 1: Plot all blocks (block_name=None)
    print("\n1. Plotting contours for ALL blocks:")
    try:
        files = processor.plot_contour_matplotlib(field_name='p', block_name=None)
        print(f"   Generated {len(files)} files: {files}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Plot single block by name
    if processor.block_names:
        first_block = processor.block_names[0]
        print(f"\n2. Plotting 3D surface for single block '{first_block}':")
        try:
            files = processor.plot_contour_plotly_surface(field_name='p', block_name=first_block)
            print(f"   Generated {len(files)} files: {files}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Example 3: Plot multiple specific blocks
    if len(processor.block_names) >= 2:
        selected_blocks = processor.block_names[:2]  # First two blocks
        print(f"\n3. Plotting line plots for selected blocks {selected_blocks}:")
        try:
            files = processor.plot_line_vs_coordinate(field_name='p', coordinate='y', block_name=selected_blocks)
            print(f"   Generated {len(files)} files: {files}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Example 4: Slice-averaged lines for all blocks
    print(f"\n4. Creating slice-averaged lines for all blocks:")
    try:
        files = processor.plot_averaged_lines(coordinate='y', block_name=None)
        print(f"   Generated {len(files)} files: {files}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 5: Overlay plot
    print(f"\n5. Creating overlay plot for all blocks:")
    try:
        file_path = processor.plot_overlay_averaged_lines(field_name='p', coordinate='y', block_name=None)
        print(f"   Generated file: {file_path}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*60)
    print("API Test Complete!")
    print("="*60)

if __name__ == "__main__":
    test_flexible_blocks()