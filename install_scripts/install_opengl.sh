#!/bin/bash

echo "Installing complete OpenGL stack for WSL..."
echo "=========================================="

# Update system
sudo apt update

# Install Mesa OpenGL implementation
sudo apt install -y \
    mesa-utils \
    mesa-utils-extra \
    mesa-va-drivers \
    mesa-vdpau-drivers \
    mesa-vulkan-drivers \
    libegl1-mesa \
    libegl1-mesa-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libgl1-mesa-dev \
    libgles2-mesa \
    libgles2-mesa-dev \
    libglapi-mesa \
    libglu1-mesa \
    libglu1-mesa-dev

# Install OSMesa (off-screen Mesa)
sudo apt install -y \
    libosmesa6 \
    libosmesa6-dev

# Install X11 and related libraries
sudo apt install -y \
    xorg-dev \
    libx11-dev \
    libxext-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    libxmu-dev \
    libxss1 \
    libgtk-3-dev

# Install virtual framebuffer
sudo apt install -y xvfb

# Install additional graphics libraries
sudo apt install -y \
    libdrm2 \
    libxcb-dri3-0 \
    libxcb-present0 \
    libxshmfence1 \
    libxxf86vm1

echo "Testing OpenGL installation..."
glxinfo | grep -i opengl || echo "glxinfo not available, but packages installed"

echo "Installation complete!"
echo "You may need to restart your terminal/WSL session."