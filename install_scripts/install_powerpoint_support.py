#!/usr/bin/env python3
"""
Installation script for PowerPoint integration dependencies

This script installs the required packages for exporting Plotly plots to PNG format
for PowerPoint compatibility.
"""

import subprocess
import sys
import importlib

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_chrome_installation():
    """Check if Chrome is installed and accessible"""
    import shutil
    
    # Common Chrome executable names/paths
    chrome_commands = [
        'google-chrome',
        'google-chrome-stable', 
        'chromium-browser',
        'chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser'
    ]
    
    for cmd in chrome_commands:
        if shutil.which(cmd):
            return True, cmd
    
    return False, None

def install_chrome_ubuntu():
    """Install Chrome on Ubuntu/WSL"""
    print("\n=== Installing Google Chrome for Ubuntu/WSL ===")
    commands = [
        "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list",
        "sudo apt update",
        "sudo apt install -y google-chrome-stable"
    ]
    
    print("The following commands will be run:")
    for cmd in commands:
        print(f"  {cmd}")
    
    response = input("\nProceed with Chrome installation? (y/n): ").lower()
    if response == 'y':
        import subprocess
        for cmd in commands:
            try:
                print(f"Running: {cmd}")
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed: {e}")
                return False
        return True
    else:
        print("Chrome installation skipped")
        return False

def main():
    print("=== PowerPoint Integration Setup ===")
    print("Installing packages for PNG export functionality...\n")
    
    # Required packages for PNG export
    packages = {
        'kaleido': 'Static image export for Plotly',
        'plotly': 'Plotly plotting library (update)',
        'psutil': 'Process utilities (helps with kaleido)'
    }
    
    installed_count = 0
    failed_packages = []
    
    for package, description in packages.items():
        print(f"Checking {package}...")
        
        if package == 'plotly':
            # Always try to update plotly to latest version
            print(f"  Updating {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
                print(f"  ✓ {package} updated successfully")
                installed_count += 1
            except subprocess.CalledProcessError:
                print(f"  ✗ Failed to update {package}")
                failed_packages.append(package)
        else:
            if check_package(package):
                print(f"  ✓ {package} is already installed")
                installed_count += 1
            else:
                print(f"  Installing {package}...")
                if install_package(package):
                    print(f"  ✓ {package} installed successfully")
                    installed_count += 1
                else:
                    print(f"  ✗ Failed to install {package}")
                    failed_packages.append(package)
    
    print(f"\n=== Installation Summary ===")
    print(f"Successfully processed: {installed_count}/{len(packages)} packages")
    
    if failed_packages:
        print(f"Failed packages: {failed_packages}")
        print("\nAlternative installation methods:")
        for package in failed_packages:
            print(f"  Manual install: pip install {package}")
    else:
        print("All packages ready!")
    
    print("\n=== Testing PNG Export ===")
    
    # First check if Chrome is available
    chrome_available, chrome_path = check_chrome_installation()
    if not chrome_available:
        print("✗ Google Chrome not found")
        print("  Kaleido requires Chrome for PNG export")
        print("\nChrome installation options:")
        print("1. Automatic (Ubuntu/WSL): Run this script with Chrome installation")
        print("2. Manual Ubuntu/WSL:")
        print("   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        print("   echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
        print("   sudo apt update && sudo apt install -y google-chrome-stable")
        print("3. Alternative: Install Chromium:")
        print("   sudo apt install chromium-browser")
        print("4. Use plotly_get_chrome:")
        print("   plotly_get_chrome")
        
        # Offer to install Chrome automatically
        try_install = input("\nTry automatic Chrome installation? (y/n): ").lower()
        if try_install == 'y':
            if install_chrome_ubuntu():
                chrome_available, chrome_path = check_chrome_installation()
                if chrome_available:
                    print(f"✓ Chrome installed successfully: {chrome_path}")
                else:
                    print("✗ Chrome installation completed but not detected")
            else:
                print("✗ Chrome installation failed")
        
        if not chrome_available:
            print("\n⚠ PNG export will not work without Chrome")
            print("  You can still use HTML files and take screenshots")
            return
    else:
        print(f"✓ Chrome found: {chrome_path}")
    
    try:
        import plotly.graph_objects as go
        
        # Create a simple test plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name='Test'))
        fig.update_layout(title='PNG Export Test')
        
        # Try to export as PNG
        try:
            fig.write_image("png_test.png", width=800, height=600)
            print("✓ PNG export test successful!")
            print("  Test file saved: png_test.png")
            
            # Clean up test file
            import os
            if os.path.exists("png_test.png"):
                os.remove("png_test.png")
                print("  Test file cleaned up")
                
        except Exception as e:
            print(f"✗ PNG export test failed: {e}")
            if "chrome" in str(e).lower() or "kaleido" in str(e).lower():
                print("  Chrome/Kaleido issue detected")
                print("  Try: plotly_get_chrome")
                print("  Or install Chrome manually")
            else:
                print("  Other PNG export issue")
                
    except ImportError as e:
        print(f"✗ Plotly import failed: {e}")
        print("  Install plotly first: pip install plotly")
    
    print("\n=== PowerPoint Integration Ready ===")
    print("You can now:")
    print("1. Run your CFD post-processing script")
    print("2. Get both HTML and PNG files automatically")
    print("3. Use PNG files directly in PowerPoint")
    print("4. Find PowerPoint-ready images in 'powerpoint_images/' folder")
    
    print("\nFor help, see: POWERPOINT_INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    main()