#!/usr/bin/env python3
import os
import sys

# Set environment variables for proper rendering
os.environ['MESA_GL_VERSION_OVERRIDE'] = '3.3'
os.environ['GALLIUM_DRIVER'] = 'llvmpipe'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

try:
    import pyvista as pv
    import vtk
    
    print("=== PyVista Installation Test ===")
    print(f"PyVista version: {pv.__version__}")
    print(f"VTK version: {vtk.vtkVersion.GetVTKVersion()}")
    
    # Configure for offscreen rendering
    pv.OFF_SCREEN = True
    pv.set_plot_theme("document")
    
    # Test basic mesh creation
    sphere = pv.Sphere()
    print(f"✓ Created sphere with {sphere.n_points} points")
    
    # Test plotting capability
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(sphere)
    
    # Try to take a screenshot to test rendering
    try:
        plotter.show(screenshot='test_render.png')
        print("✓ Offscreen rendering successful - test_render.png created")
        os.remove('test_render.png')  # Clean up
    except Exception as e:
        print(f"✗ Rendering test failed: {e}")
        
    plotter.close()
    
    print("=== Test Results ===")
    print("✓ PyVista basic functionality: PASS")
    print("✓ VTK backend: AVAILABLE")
    
    # Check available render windows
    print("\n=== Available Render Windows ===")
    print(f"OpenGL: {hasattr(vtk, 'vtkOpenGLRenderWindow')}")
    print(f"OSMesa: {hasattr(vtk, 'vtkOSMesaRenderWindow')}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Runtime error: {e}")
    sys.exit(1)
    
print("\n🎉 PyVista installation test completed successfully!")
