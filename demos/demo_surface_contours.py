#!/usr/bin/env python3
"""
Demonstration of surface contour plotting functionality
"""

from VTKPostProcessor import VTKPostProcessor

def demo_surface_contours():
    """Demonstrate the new surface contour plotting capabilities"""
    
    # Initialize processor - adjust path to your VTU file
    vtk_file = 'path_to_your.vtu'  # Replace with actual path
    processor = VTKPostProcessor(vtk_file)
    
    print("\n" + "="*70)
    print("Surface Contour Plotting Demo")
    print("="*70)
    
    # Show available blocks
    print(f"\nAvailable blocks: {processor.block_names}")
    
    # 1. Surface contours for single block
    if processor.block_names:
        first_block = processor.block_names[0]
        print(f"\n1. Creating surface contours for block '{first_block}':")
        
        # Create contours projected on different axes
        for projection in ['x', 'y', 'z']:
            try:
                files = processor.plot_surface_contours_plotly(
                    field_name='p',
                    block_name=first_block,
                    projection_axis=projection
                )
                print(f"   {projection.upper()}-projection: {files}")
            except Exception as e:
                print(f"   Error with {projection}-projection: {e}")
    
    # 2. Surface contours for all blocks
    print(f"\n2. Creating surface contours for all blocks (Z-projection):")
    try:
        files = processor.plot_surface_contours_plotly(
            field_name='p',
            block_name=None,  # All blocks
            projection_axis='z'
        )
        print(f"   Generated {len(files)} surface contour files")
        for file_path in files:
            print(f"   - {file_path}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Compare with 3D surface plots
    print(f"\n3. Creating 3D surface plots for comparison:")
    try:
        files = processor.plot_contour_plotly_surface(
            field_name='p',
            block_name=processor.block_names[0]  # First block
        )
        print(f"   3D Surface files: {files}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Multiple variables with surface contours
    print(f"\n4. Creating surface contours for multiple variables:")
    try:
        # Get available variables
        variables = processor.get_variable_names(block_name=processor.block_names[0])
        cell_vars = variables['cell_data'][:3]  # First 3 variables
        
        for var in cell_vars:
            try:
                files = processor.plot_surface_contours_plotly(
                    field_name=var,
                    block_name=processor.block_names[0],
                    projection_axis='z'  # Z-projection (X-Y plane)
                )
                print(f"   {var}: {files}")
            except Exception as e:
                print(f"   Error with {var}: {e}")
                
    except Exception as e:
        print(f"   Error getting variables: {e}")
    
    print("\n" + "="*70)
    print("Surface Contour Demo Complete!")
    print("="*70)
    
    print("\nSurface Contour vs 3D Surface:")
    print("------------------------------")
    print("🔹 Surface Contours:")
    print("   - 2D contour lines projected on coordinate planes")
    print("   - Easier to read specific values")
    print("   - Better for quantitative analysis")
    print("   - Can project on X-Y, X-Z, or Y-Z planes")
    print("")
    print("🔹 3D Surfaces:")
    print("   - True 3D surface visualization")
    print("   - Better for overall structure understanding")
    print("   - Interactive 3D viewing")
    print("   - Good for presentations")

if __name__ == "__main__":
    demo_surface_contours()