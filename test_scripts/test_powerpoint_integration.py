#!/usr/bin/env python3
"""
Test script for PowerPoint integration functionality

This script tests the PNG export capabilities and demonstrates how to get
CFD plots ready for PowerPoint presentations.
"""

from VTKPostProcessor import CFDPostProcessor
import os

def test_powerpoint_integration():
    """Test PowerPoint integration features"""
    
    print("=== PowerPoint Integration Test ===")
    
    # Check if kaleido is available
    try:
        import plotly.graph_objects as go
        
        # Test basic PNG export capability
        test_fig = go.Figure()
        test_fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name='Test'))
        test_fig.update_layout(title='PNG Export Test', width=800, height=600)
        
        try:
            test_fig.write_image("test_png_export.png")
            print("✓ Kaleido PNG export is working")
            os.remove("test_png_export.png")  # Clean up
            png_available = True
        except Exception as e:
            print(f"✗ PNG export not available: {e}")
            print("  Install kaleido for PNG export: pip install kaleido")
            png_available = False
            
    except ImportError:
        print("✗ Plotly not available")
        return
    
    # Create processor and test data
    processor = CFDPostProcessor('geom_vol.vtm')
    
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
    
    print(f"Variables: {sorted(all_variables)}")
    
    # Create test directories
    os.makedirs('powerpoint_test', exist_ok=True)
    os.makedirs('powerpoint_test/images', exist_ok=True)
    
    print("\n=== PowerPoint Integration Test ===")
    
    if not all_variables:
        print("No variables found - cannot test PowerPoint integration")
        return
    
    # Test with first available variable
    test_variable = list(all_variables)[0]
    print(f"Testing with variable: {test_variable}")
    
    # Find blocks that have this variable
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
    
    try:
        # Test the combined geometry surface contours with PowerPoint export
        print(f"\nCreating PowerPoint-ready plot for '{test_variable}'...")
        
        result = processor.plot_geometry_surface_contours_combined(
            field_name=test_variable,
            block_name=blocks_with_variable,
            data_type='cell',
            save_path=f'powerpoint_test/test_{test_variable}_combined.html'
        )
        
        if isinstance(result, dict):
            print(f"✓ HTML file: {result['html']}")
            if result['png']:
                print(f"✓ PNG file: {result['png']}")
                
                # Copy to images folder for easy access
                import shutil
                png_filename = os.path.basename(result['png'])
                powerpoint_png = f'powerpoint_test/images/{png_filename}'
                shutil.copy2(result['png'], powerpoint_png)
                print(f"✓ PowerPoint-ready PNG: {powerpoint_png}")
                
                # Get PNG file size and dimensions
                try:
                    from PIL import Image
                    with Image.open(powerpoint_png) as img:
                        width, height = img.size
                        print(f"  Image dimensions: {width}×{height} pixels")
                except ImportError:
                    print("  Install Pillow to check image dimensions: pip install Pillow")
                
                file_size = os.path.getsize(powerpoint_png) / 1024  # KB
                print(f"  File size: {file_size:.1f} KB")
                
            else:
                print("✗ PNG export failed - kaleido not available")
        else:
            print(f"✓ Plot created: {result}")
            print("  (Using older version without PNG export)")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return
    
    print("\n=== PowerPoint Usage Instructions ===")
    print("To use these plots in PowerPoint:")
    print("1. Open PowerPoint")
    print("2. Insert → Pictures → This Device")
    print("3. Navigate to 'powerpoint_test/images/' folder")
    print("4. Select the PNG file and insert")
    print("5. Resize as needed in PowerPoint")
    
    print("\n=== Alternative Methods ===")
    if not png_available:
        print("Since PNG export is not available:")
        print("1. Open the HTML file in a web browser")
        print("2. Adjust the view as desired (rotate, zoom)")
        print("3. Take a screenshot (Windows: Win+Shift+S)")
        print("4. Paste directly into PowerPoint")
    
    print("\n=== File Summary ===")
    print("Generated files:")
    for root, dirs, files in os.walk('powerpoint_test'):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"  {file_path}")
    
    print("\n=== Setup for Production Use ===")
    print("For full PowerPoint integration:")
    print("1. Install kaleido: pip install kaleido")
    print("2. Run the main post-processing script")
    print("3. Check 'powerpoint_images/' folder for PNG files")
    print("4. Use PNG files directly in presentations")

if __name__ == "__main__":
    test_powerpoint_integration()