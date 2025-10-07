#!/usr/bin/env python3
"""
Simple PowerPoint Integration Setup Script

This script installs the required packages and provides guidance for PNG export.
"""

import subprocess
import sys
import importlib
import shutil

def run_command(command):
    """Run a command and return success status"""
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, upgrade=False):
    """Install or upgrade a package using pip"""
    try:
        if upgrade:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        else:
            cmd = [sys.executable, "-m", "pip", "install", package_name]
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def check_chrome():
    """Check if Chrome is available"""
    chrome_commands = ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']
    for cmd in chrome_commands:
        if shutil.which(cmd):
            return True, cmd
    return False, None

def main():
    print("=== Simple PowerPoint Integration Setup ===")
    print()
    
    # Step 1: Install/upgrade required packages
    print("📦 Installing required packages...")
    packages = ['kaleido', 'plotly', 'psutil']
    
    for package in packages:
        print(f"Installing {package}...")
        if package == 'plotly':
            success = install_package(package, upgrade=True)
        else:
            success = install_package(package)
        
        if success:
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
    
    print()
    
    # Step 2: Check Chrome
    print("🌐 Checking Chrome installation...")
    chrome_available, chrome_path = check_chrome()
    
    if chrome_available:
        print(f"  ✅ Chrome found: {chrome_path}")
    else:
        print("  ❌ Chrome not found")
        print()
        print("Chrome is required for PNG export. Install options:")
        print("1. Ubuntu/WSL: sudo apt install google-chrome-stable")
        print("2. Alternative: sudo apt install chromium-browser")
        print("3. Manual download from Google Chrome website")
        print("4. Use: plotly_get_chrome")
        print()
    
    # Step 3: Test PNG export
    print("🧪 Testing PNG export...")
    
    try:
        import plotly.graph_objects as go
        
        # Create test figure
        fig = go.Figure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name='Test')
        fig.update_layout(title='PNG Export Test', width=600, height=400)
        
        # Try PNG export
        try:
            fig.write_image("test_export.png")
            print("  ✅ PNG export test successful!")
            
            # Clean up
            import os
            if os.path.exists("test_export.png"):
                os.remove("test_export.png")
            
        except Exception as e:
            print(f"  ❌ PNG export failed: {e}")
            if chrome_available:
                print("  Chrome is installed but PNG export still failed")
                print("  Try: pip install --upgrade kaleido plotly")
            else:
                print("  Install Chrome first, then try again")
    
    except ImportError:
        print("  ❌ Plotly not available")
    
    print()
    
    # Step 4: Summary
    print("📋 Setup Summary:")
    print()
    
    if chrome_available and check_package('kaleido') and check_package('plotly'):
        print("✅ PowerPoint integration is ready!")
        print("   - Run your CFD post-processing script")
        print("   - PNG files will be generated automatically")
        print("   - Look in 'powerpoint_images/' folder")
        print("   - Insert PNG files directly into PowerPoint")
    else:
        print("⚠️  Setup incomplete:")
        if not check_package('kaleido'):
            print("   - Install kaleido: pip install kaleido")
        if not check_package('plotly'):
            print("   - Install plotly: pip install plotly")
        if not chrome_available:
            print("   - Install Chrome (see options above)")
    
    print()
    print("🎯 Next steps:")
    print("1. Fix any missing components above")
    print("2. Run: python scripts/post_processing_clean.py")
    print("3. Check output in 'powerpoint_images/' folder")
    print("4. Insert PNG files into PowerPoint presentations")

if __name__ == "__main__":
    main()