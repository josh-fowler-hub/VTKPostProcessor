# Quick Fix for PNG Export Issue

## Problem
Kaleido requires Google Chrome to be installed for PNG export functionality.

## Solution Options

### Option 1: Install Chrome (Recommended)
```bash
# Run the Chrome installation script
cd install_scripts
chmod +x install_chrome.sh
./install_chrome.sh
```

### Option 2: Manual Chrome Installation
```bash
# Add Google's signing key
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Add Chrome repository
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update and install
sudo apt update
sudo apt install -y google-chrome-stable
```

### Option 3: Install Chromium (Alternative)
```bash
sudo apt install chromium-browser
```

### Option 4: Use Plotly's Chrome Installer
```bash
plotly_get_chrome
```

### Option 5: Fix Plotly Installation
```bash
# Fix the plotly upgrade issue
pip install --upgrade plotly
```

## After Chrome Installation

### Test PNG Export
```bash
cd install_scripts
python install_powerpoint_support.py
```

### Run Your CFD Analysis
```bash
cd scripts
python post_processing_clean.py
```

## Expected Results After Fix

✅ **With Chrome installed:**
- Both HTML and PNG files generated automatically
- PNG files copied to `powerpoint_images/` folder
- Ready for PowerPoint insertion

❌ **Without Chrome:**
- Only HTML files generated
- Need to use screenshot method for PowerPoint
- Manual conversion required

## PowerPoint Workflow After Fix

1. **Install Chrome** (one-time setup)
2. **Run post-processing**: `python scripts/post_processing_clean.py`
3. **Check output**: Look in `powerpoint_images/` folder
4. **Insert in PowerPoint**: Insert → Pictures → Browse to PNG files

## Troubleshooting

### If Chrome installation fails:
- Try Chromium: `sudo apt install chromium-browser`
- Use WSL2 instead of WSL1
- Update WSL: `wsl --update`

### If PNG export still fails:
- Restart terminal after Chrome installation
- Check Chrome version: `google-chrome --version`
- Try alternative: `pip install selenium` + manual screenshot

### For presentation immediately:
- Open HTML files in browser
- Take screenshots (Win+Shift+S on Windows)
- Paste directly into PowerPoint

The Chrome requirement is a one-time setup issue. Once installed, you'll get automatic PNG generation for all future CFD visualizations!