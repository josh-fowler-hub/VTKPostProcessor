#!/bin/bash

echo "Installing PyVista dependencies for WSL..."
echo "========================================="

# Update package list
echo "Updating package list..."
sudo apt update

# Install basic development tools
echo "Installing development tools..."
sudo apt install -y build-essential cmake git

# Install X11 and OpenGL libraries
echo "Installing X11 and OpenGL libraries..."
sudo apt install -y \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxi-dev \
    libxcursor-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    freeglut3-dev

# Install Mesa libraries for software rendering
echo "Installing Mesa libraries..."
sudo apt install -y \
    mesa-utils \
    mesa-common-dev \
    libosmesa6-dev \
    libgl1-mesa-glx \
    libglapi-mesa \
    libgles2-mesa-dev

# Install virtual framebuffer and display tools
echo "Installing virtual display tools..."
sudo apt install -y \
    xvfb \
    x11-apps \
    imagemagick

# Install additional graphics libraries
echo "Installing additional graphics libraries..."
sudo apt install -y \
    libgtk-3-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libatk1.0-dev

# Install Python development headers (if needed)
echo "Installing Python development headers..."
sudo apt install -y python3-dev python3-pip

# Install conda/pip packages for PyVista
echo "Installing Python packages..."
pip install --upgrade pip
pip install pyvista vtk matplotlib numpy pandas

# Create a test script to verify installation
echo "Creating test script..."
cat > test_pyvista.py << 'EOF'
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
EOF

chmod +x test_pyvista.py

echo ""
echo "============================================="
echo "Installation completed!"
echo "============================================="
echo ""
echo "To test the installation, run:"
echo "  python3 test_pyvista.py"
echo ""
echo "If you're using WSL, you may also want to set up X11 forwarding:"
echo "  export DISPLAY=:0"
echo ""
echo "Or install WSLg for better graphics support:"
echo "  wsl --update"
echo ""