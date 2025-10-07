# Modular Post Processing Script - Usage Guide

## Overview
The `post_processing_clean.py` script is now organized into independent, commentable blocks for maximum flexibility. Each visualization type can be enabled or disabled independently.

## Script Structure

### **BLOCK 1: SLICE AND AVERAGE DATA GENERATION**
```python
# =============================================================================
# BLOCK 1: SLICE AND AVERAGE DATA GENERATION
# Comment out this entire block if averaged data already exists
# =============================================================================
```
- **Purpose**: Computes slice-averaged data and saves CSV files
- **When to comment out**: After first run when CSV files exist
- **Time**: Slowest block (heavy computation)

### **BLOCK 2: LOAD EXISTING AVERAGED DATA**
```python
# =============================================================================
# BLOCK 2: LOAD EXISTING AVERAGED DATA (Alternative to Block 1)
# Uncomment this block if you want to load pre-existing averaged data
# =============================================================================
```
- **Purpose**: Loads pre-existing CSV files
- **When to uncomment**: When skipping Block 1
- **Time**: Very fast (file loading only)

### **BLOCK 3: VISUALIZATION SETUP**
```python
# =============================================================================
# BLOCK 3: VISUALIZATION GENERATION - SETUP
# =============================================================================
```
- **Purpose**: Analyzes blocks and collects variable information
- **Always needed**: Required for all visualization blocks
- **Time**: Fast (metadata collection)

### **BLOCK 4: 2D CONTOUR PLOTS (MATPLOTLIB)**
```python
# =============================================================================
# BLOCK 4: 2D CONTOUR PLOTS (MATPLOTLIB)
# Comment out this entire block to skip 2D contour generation
# =============================================================================
```
- **Purpose**: Creates 2D matplotlib contour plots
- **Output**: `contour_plots/contour_{var}_{block}.png`
- **When to comment out**: If you don't need 2D contours
- **Time**: Medium (one plot per variable per block)

### **BLOCK 5: AVERAGED LINE PLOTS**
```python
# =============================================================================
# BLOCK 5: AVERAGED LINE PLOTS (FROM SLICE DATA)
# Comment out this entire block to skip averaged line plot generation
# =============================================================================
```
- **Purpose**: Creates line plots from slice-averaged data
- **Output**: `line_plots/averaged_lines_{block}.png`
- **When to comment out**: If you don't need individual line plots
- **Time**: Fast (uses pre-computed averages)

### **BLOCK 6: 3D SURFACE PLOTS**
```python
# =============================================================================
# BLOCK 6: 3D SURFACE PLOTS (PLOTLY)
# Comment out this entire block to skip 3D surface generation
# =============================================================================
```
- **Purpose**: Creates interactive 3D surface visualizations
- **Output**: `3d_plots/surface_{var}_{block}.html`
- **When to comment out**: If you don't need 3D surfaces
- **Time**: Medium (interpolation required)

### **BLOCK 7: SURFACE CONTOUR PLOTS**
```python
# =============================================================================
# BLOCK 7: SURFACE CONTOUR PLOTS (PLOTLY 2D PROJECTIONS)
# Comment out this entire block to skip surface contour generation
# =============================================================================
```
- **Purpose**: Creates 2D contour projections on coordinate planes
- **Output**: `3d_plots/surface_contour_{var}_{proj}proj_{block}.html`
- **When to comment out**: If you don't need surface contours
- **Time**: Medium (creates X, Y, Z projections)

### **BLOCK 8: OVERLAY PLOTS**
```python
# =============================================================================
# BLOCK 8: OVERLAY PLOTS FROM AVERAGED DATA (Single Variable, All Blocks)
# Comment out this entire block to skip overlay plot generation
# =============================================================================
```
- **Purpose**: Creates comparison plots (single variable across all blocks)
- **Output**: `line_plots/overlay_{var}_all_blocks.png`
- **When to comment out**: If you don't need block comparisons
- **Time**: Fast (uses pre-computed averages)

## Usage Scenarios

### **Scenario 1: Complete First Run**
```python
# Block 1: ACTIVE (generate averaged data)
# Block 2: COMMENTED OUT
# Block 3: ACTIVE (always needed)
# Block 4: ACTIVE (2D contours)
# Block 5: ACTIVE (line plots)
# Block 6: ACTIVE (3D surfaces)
# Block 7: ACTIVE (surface contours)
# Block 8: ACTIVE (overlays)
```
**Result**: Generates all data and all visualizations

### **Scenario 2: Visualization Updates Only**
```python
# Block 1: COMMENTED OUT
# Block 2: ACTIVE (load existing data)
# Block 3: ACTIVE (always needed)
# Block 4: ACTIVE (2D contours)
# Block 5: ACTIVE (line plots)
# Block 6: ACTIVE (3D surfaces)
# Block 7: ACTIVE (surface contours)
# Block 8: ACTIVE (overlays)
```
**Result**: Fast regeneration of all plots using existing data

### **Scenario 3: Only 2D Analysis**
```python
# Block 1: COMMENTED OUT
# Block 2: ACTIVE (load existing data)
# Block 3: ACTIVE (always needed)
# Block 4: ACTIVE (2D contours)
# Block 5: ACTIVE (line plots)
# Block 6: COMMENTED OUT (skip 3D surfaces)
# Block 7: COMMENTED OUT (skip surface contours)
# Block 8: ACTIVE (overlays)
```
**Result**: Only 2D visualizations (contours, lines, overlays)

### **Scenario 4: Only 3D Analysis**
```python
# Block 1: COMMENTED OUT
# Block 2: ACTIVE (load existing data)
# Block 3: ACTIVE (always needed)
# Block 4: COMMENTED OUT (skip 2D contours)
# Block 5: COMMENTED OUT (skip line plots)
# Block 6: ACTIVE (3D surfaces)
# Block 7: ACTIVE (surface contours)
# Block 8: COMMENTED OUT (skip overlays)
```
**Result**: Only 3D visualizations (surfaces and surface contours)

### **Scenario 5: Quick Overview**
```python
# Block 1: COMMENTED OUT
# Block 2: ACTIVE (load existing data)
# Block 3: ACTIVE (always needed)
# Block 4: COMMENTED OUT (skip 2D contours)
# Block 5: COMMENTED OUT (skip line plots)
# Block 6: COMMENTED OUT (skip 3D surfaces)
# Block 7: COMMENTED OUT (skip surface contours)
# Block 8: ACTIVE (overlays only)
```
**Result**: Only overlay plots for quick comparison

## File Organization

```
📁 Project Directory/
├── 📁 averaged_data/          # Block 1 output
│   └── *_avg.csv
├── 📁 contour_plots/          # Block 4 output
│   └── contour_*_*.png
├── 📁 line_plots/             # Block 5 & 8 output
│   ├── averaged_lines_*.png
│   └── overlay_*_all_blocks.png
└── 📁 3d_plots/               # Block 6 & 7 output
    ├── surface_*_*.html
    └── surface_contour_*_*proj_*.html
```

## Performance Optimization

### **Time Estimates** (typical CFD dataset):
- **Block 1**: 5-10 minutes (slice computation)
- **Block 2**: 5-10 seconds (file loading)
- **Block 3**: 10-20 seconds (metadata)
- **Block 4**: 2-5 minutes (2D contours)
- **Block 5**: 30-60 seconds (line plots)
- **Block 6**: 1-3 minutes (3D surfaces)
- **Block 7**: 2-4 minutes (surface contours)
- **Block 8**: 30-60 seconds (overlays)

### **Speed Tips**:
1. **After first run**: Comment Block 1, uncomment Block 2
2. **For quick tests**: Comment Blocks 4, 6, 7 (keep only lines/overlays)
3. **For presentations**: Comment Blocks 4, 5 (keep only 3D visualizations)
4. **For analysis**: Comment Blocks 6, 7 (keep only 2D visualizations)

## Example Workflows

### **Daily Development Workflow**:
```bash
# Day 1: Initial analysis
python post_processing_clean.py  # All blocks active

# Day 2+: Update visualizations only
# Edit script: Comment Block 1, Uncomment Block 2
python post_processing_clean.py  # Much faster
```

### **Publication Workflow**:
```bash
# Generate all plots for review
python post_processing_clean.py  # All visualization blocks

# Generate only high-quality plots for paper
# Comment out unwanted blocks, keep only needed visualizations
python post_processing_clean.py
```

### **Debugging Workflow**:
```bash
# Quick check with overlays only
# Comment Blocks 4,5,6,7 (keep only Block 8)
python post_processing_clean.py  # Very fast overview
```

## Benefits of Modular Structure

1. **⚡ Speed**: Skip expensive computations after first run
2. **🎯 Targeted**: Generate only needed visualization types
3. **💾 Storage**: Avoid generating unwanted large files
4. **🔧 Debugging**: Isolate issues to specific visualization types
5. **📊 Customization**: Easy to add new visualization blocks
6. **🔄 Iterative**: Perfect for iterative analysis workflows

## Adding Custom Blocks

To add a new visualization type:

```python
# =============================================================================
# BLOCK 9: CUSTOM ANALYSIS
# Comment out this entire block to skip custom analysis
# =============================================================================
print(f"\n=== BLOCK 9: Creating Custom Analysis ===")
for block_name in block_names:
    if block_name in block_variables:
        print(f"\nCustom analysis for {block_name}...")
        # Your custom code here
        # Use: all_dataframes[block_name] for averaged data
        # Use: block_variables[block_name]['cell_data'] for variables
```

This modular structure gives you complete control over your post-processing workflow!