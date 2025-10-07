#!/bin/bash
# Chrome Installation Script for Ubuntu/WSL
# This script installs Google Chrome for PNG export functionality

echo "=== Installing Google Chrome for PNG Export ==="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "❌ This script is for Ubuntu/Debian systems"
    echo "For other systems, install Chrome manually"
    exit 1
fi

# Check if Chrome is already installed
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome is already installed"
    google-chrome --version
    exit 0
fi

echo "📦 Installing Google Chrome..."
echo ""

# Add Google's signing key
echo "Adding Google signing key..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Add Chrome repository
echo "Adding Chrome repository..."
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update package list
echo "Updating package list..."
sudo apt update

# Install Chrome
echo "Installing Google Chrome..."
sudo apt install -y google-chrome-stable

# Verify installation
if command -v google-chrome &> /dev/null; then
    echo ""
    echo "✅ Google Chrome installed successfully!"
    google-chrome --version
    echo ""
    echo "🎉 PNG export should now work with Kaleido"
    echo ""
    echo "Test with:"
    echo "  python install_powerpoint_support.py"
else
    echo ""
    echo "❌ Chrome installation failed"
    echo ""
    echo "Alternative installation:"
    echo "  sudo apt install chromium-browser"
    echo ""
    echo "Or try:"
    echo "  plotly_get_chrome"
fi