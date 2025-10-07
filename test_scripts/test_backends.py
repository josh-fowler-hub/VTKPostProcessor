#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from VTKPostProcessor import CFDPostProcessor

def test_contour_backends():
    """Test different contour plotting backends"""
    print("Testing alternative contour plotting backends...")
    print("=" * 60)
    
    try:
        # Load the data
        processor = CFDPostProcessor('inner_surface.vtm')
        print(f"Loaded dataset with {len(processor.data)} blocks")
        
        # Get available variables
        vars_info = processor.get_variable_names(block_index=0, verbose=True)
        cell_vars = vars_info['cell_data']
        
        if not cell_vars:
            print("No cell data variables found!")
            return
        
        # Use first available variable for testing
        test_var = cell_vars[0]
        print(f"\nTesting with variable: {test_var}")
        
        # Test matplotlib backend
        print("\n1. Testing Matplotlib backend...")
        try:
            result = processor.plot_contour_alternative(
                block_id=0, 
                field=test_var, 
                n_contours=10, 
                data_type='cell', 
                backend='matplotlib'
            )
            if result:
                print(f"✓ Matplotlib contour plot created: {result}")
            else:
                print("✗ Matplotlib backend failed")
        except Exception as e:
            print(f"✗ Matplotlib backend error: {e}")
        
        # Test plotly backend
        print("\n2. Testing Plotly backend...")
        try:
            result = processor.plot_contour_alternative(
                block_id=0, 
                field=test_var, 
                n_contours=10, 
                data_type='cell', 
                backend='plotly'
            )
            if result:
                print(f"✓ Plotly plot created: {result}")
            else:
                print("✗ Plotly backend failed")
        except Exception as e:
            print(f"✗ Plotly backend error: {e}")
        
        # Test ASCII backend
        print("\n3. Testing ASCII backend...")
        try:
            result = processor.plot_contour_alternative(
                block_id=0, 
                field=test_var, 
                n_contours=8, 
                data_type='cell', 
                backend='ascii'
            )
            if result:
                print(f"✓ ASCII contour plot created: {result}")
                # Show first few lines
                with open(result, 'r') as f:
                    lines = f.readlines()[:10]
                    print("First few lines of ASCII plot:")
                    for line in lines:
                        print("  " + line.strip())
            else:
                print("✗ ASCII backend failed")
        except Exception as e:
            print(f"✗ ASCII backend error: {e}")
        
        # Test auto backend
        print("\n4. Testing Auto backend selection...")
        try:
            result = processor.plot_contour_alternative(
                block_id=0, 
                field=test_var, 
                n_contours=10, 
                data_type='cell', 
                backend='auto'
            )
            if result:
                print(f"✓ Auto backend succeeded: {result}")
            else:
                print("✗ Auto backend failed")
        except Exception as e:
            print(f"✗ Auto backend error: {e}")
        
        print("\n" + "=" * 60)
        print("Backend testing complete!")
        
        # Show available files
        import glob
        plot_files = glob.glob("contour_*")
        if plot_files:
            print(f"\nGenerated {len(plot_files)} visualization files:")
            for f in plot_files:
                print(f"  - {f}")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_contour_backends()