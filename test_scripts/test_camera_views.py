#!/usr/bin/env python3
"""
Camera View Demonstration Script

This script shows all available camera orientations for CFD plots
and generates examples with different views.
"""

from VTKPostProcessor import CFDPostProcessor
import os

def test_camera_views():
    """Test different camera orientations"""
    
    print("=== Camera View Demonstration ===")
    
    # Create processor
    processor = CFDPostProcessor('geom_vol.vtm')
    
    # Get available data
    print("\n=== Available Data ===")
    block_names = processor.get_block_names()
    print(f"Blocks: {block_names}")
    
    # Get variables
    all_variables = set()
    block_variables = {}
    
    for block_name in block_names:
        try:
            cell_vars, point_vars = processor.get_available_variables(block_name=block_name)
            block_variables[block_name] = {'cell_data': cell_vars, 'point_data': point_vars}
            all_variables.update(cell_vars)
        except Exception as e:
            print(f"Could not get variables for {block_name}: {e}")
    
    if not all_variables:
        print("No variables found - cannot test camera views")
        return
    
    # Use first available variable
    test_variable = list(all_variables)[0]
    print(f"\nTesting with variable: {test_variable}")
    
    # Find blocks with this variable
    blocks_with_variable = []
    for block_name in block_names:
        if block_name in block_variables:
            cell_vars = block_variables[block_name]['cell_data']
            if test_variable in cell_vars:
                blocks_with_variable.append(block_name)
    
    if not blocks_with_variable:
        print(f"No blocks found with variable {test_variable}")
        return
    
    print(f"Blocks with {test_variable}: {blocks_with_variable}")
    
    # Create output directory
    os.makedirs('camera_views_demo', exist_ok=True)
    
    # Available camera views
    camera_views = {
        'isometric': 'Standard isometric view (recommended for presentations)',
        'front': 'Front view (looking along Y-axis)',
        'side': 'Side view (looking along X-axis)',
        'top': 'Top view (looking down Z-axis)',
        'back': 'Back view',
        'bottom': 'Bottom view',
        'perspective': 'Default perspective view',
        'close_isometric': 'Closer isometric view',
        'far_isometric': 'Farther isometric view'
    }
    
    print(f"\n=== Testing Camera Views ===")
    print("Generating plots with different camera orientations...")
    
    successful_views = []
    
    for view_name, description in camera_views.items():
        print(f"\nCreating {view_name} view...")
        print(f"  Description: {description}")
        
        try:
            result = processor.plot_geometry_surface_contours_combined(
                field_name=test_variable,
                block_name=blocks_with_variable,
                data_type='cell',
                save_path=f'camera_views_demo/{test_variable}_{view_name}_view.html',
                camera_view=view_name
            )
            
            if isinstance(result, dict):
                print(f"  ✓ HTML: {result['html']}")
                if result['png']:
                    print(f"  ✓ PNG: {result['png']}")
                else:
                    print(f"  ⚠ PNG export failed (install Chrome/kaleido)")
            else:
                print(f"  ✓ Created: {result}")
            
            successful_views.append(view_name)
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    # Test custom camera position
    print(f"\nTesting custom camera position...")
    try:
        custom_camera = {
            'eye': dict(x=2.0, y=0.5, z=1.0),  # Custom position
            'center': dict(x=0, y=0, z=0),     # Look at origin
            'up': dict(x=0, y=0, z=1)          # Z-axis up
        }
        
        result = processor.plot_geometry_surface_contours_combined(
            field_name=test_variable,
            block_name=blocks_with_variable,
            data_type='cell',
            save_path=f'camera_views_demo/{test_variable}_custom_view.html',
            camera_view=custom_camera
        )
        
        print(f"  ✓ Custom camera view created")
        successful_views.append('custom')
        
    except Exception as e:
        print(f"  ✗ Custom camera failed: {e}")
    
    print(f"\n=== Results Summary ===")
    print(f"Successfully created {len(successful_views)} views: {successful_views}")
    
    print(f"\nGenerated files:")
    if os.path.exists('camera_views_demo'):
        for file in sorted(os.listdir('camera_views_demo')):
            file_path = os.path.join('camera_views_demo', file)
            print(f"  {file_path}")
    
    print(f"\n=== Camera View Guide ===")
    print("Available camera views for your CFD plots:")
    print()
    
    for view_name, description in camera_views.items():
        print(f"🎥 '{view_name}'")
        print(f"   {description}")
        print()
    
    print("🎯 Recommended for PowerPoint presentations:")
    print("   • 'isometric' - Best general view showing all dimensions")
    print("   • 'front' - Good for showing main flow direction")
    print("   • 'side' - Good for profile views")
    print()
    
    print("📝 Usage in your scripts:")
    print("   processor.plot_geometry_surface_contours_combined(")
    print("       field_name='pressure',")
    print("       camera_view='isometric'  # or any other view")
    print("   )")
    print()
    
    print("⚙️ Custom camera positions:")
    print("   custom_camera = {")
    print("       'eye': dict(x=2.0, y=1.0, z=1.5),")
    print("       'center': dict(x=0, y=0, z=0),")
    print("       'up': dict(x=0, y=0, z=1)")
    print("   }")
    print("   processor.plot_geometry_surface_contours_combined(")
    print("       field_name='pressure',")
    print("       camera_view=custom_camera")
    print("   )")

if __name__ == "__main__":
    test_camera_views()