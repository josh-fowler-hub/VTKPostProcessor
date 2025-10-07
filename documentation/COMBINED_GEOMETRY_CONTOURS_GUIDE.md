# Combined Geometry Surface Contour Visualization Guide

## Overview
The new `plot_geometry_surface_contours_combined()` method creates **single plots that combine all blocks** showing the same variable. This gives you a complete view of how each field variable varies across your entire CFD geometry.

## What's New

### Previous Behavior (Individual Block Plots)
- `plot_geometry_surface_contours()` created separate plots for each block
- If you had 5 blocks, you got 5 separate HTML files
- Hard to compare field values between blocks

### New Behavior (Combined Block Plots) 
- `plot_geometry_surface_contours_combined()` creates one plot per variable
- All blocks that contain a variable are shown in the same plot  
- Consistent color scale across all blocks
- Easy comparison of field values between different parts of geometry

## Updated Post-Processing Script

The modular script (`post_processing_clean.py`) **BLOCK 8** now works as follows:

```python
# =============================================================================
# BLOCK 8: GEOMETRY SURFACE CONTOUR PLOTS (PLOTLY 3D MESH)
# Creates ONE plot per variable, combining ALL blocks
# =============================================================================

# For each variable found across all blocks:
for var_name in sorted(all_variables):
    # Find which blocks have this variable
    blocks_with_variable = [block for block in blocks if variable in block]
    
    # Create single combined plot showing all blocks with this variable
    processor.plot_geometry_surface_contours_combined(
        field_name=var_name,
        block_name=blocks_with_variable,  # List of blocks
        save_path=f'geometry_surface_contour_combined_{var_name}_all_blocks.html'
    )
```

## Output Structure

### Files Generated
```
surface_contours/
├── geometry_surface_contour_combined_pressure_all_blocks.html
├── geometry_surface_contour_combined_velocity_all_blocks.html  
├── geometry_surface_contour_combined_temperature_all_blocks.html
└── geometry_surface_contour_combined_turbulence_all_blocks.html
```

### What Each File Contains
- **One interactive 3D plot** per variable
- **All blocks** that contain that variable in the same scene
- **Consistent color scale** showing min/max across all blocks
- **Block legends** to identify which mesh is which block
- **Interactive controls** for rotation, zoom, pan

## Example Usage

### Basic Combined Plot
```python
from VTKPostProcessor import CFDPostProcessor

processor = CFDPostProcessor('your_data.vtm')

# Create combined plot for pressure across all blocks
file_path = processor.plot_geometry_surface_contours_combined(
    field_name='p',           # pressure
    block_name=None,          # all blocks (or specify list)
    data_type='cell'
)
```

### Specific Blocks Only
```python
# Combine only specific blocks
file_path = processor.plot_geometry_surface_contours_combined(
    field_name='velocity_magnitude',
    block_name=['Block1', 'Block3', 'Block5'],  # specific blocks
    data_type='cell'
)
```

### Variable-Specific Processing
```python
# Get all variables and create combined plots
all_variables = {'pressure', 'velocity', 'temperature'}

for variable in all_variables:
    # Find blocks that have this variable
    blocks_with_var = find_blocks_with_variable(variable)
    
    if blocks_with_var:
        processor.plot_geometry_surface_contours_combined(
            field_name=variable,
            block_name=blocks_with_var,
            save_path=f'combined_{variable}_all_blocks.html'
        )
```

## Key Features

### Consistent Color Mapping
- All blocks use the same color scale for direct comparison
- Color bar shows min/max values across ALL blocks
- Makes it easy to see which regions have high/low values

### Interactive Visualization
- **Rotate**: Click and drag to view from different angles
- **Zoom**: Mouse wheel or pinch to zoom in/out
- **Pan**: Hold shift and drag to pan
- **Block Toggle**: Click legend to show/hide specific blocks
- **Hover Info**: Mouse over surfaces to see exact values

### Smart Block Detection
- Automatically finds which blocks contain each variable
- Only includes blocks that actually have the requested field
- Handles cases where not all blocks have all variables

## Comparison: Individual vs Combined

### When to Use Individual Plots
```python
processor.plot_geometry_surface_contours()  # Original method
```
- **Detailed analysis** of specific blocks
- **Isolating** individual components
- **High-resolution** views of single block
- **Debugging** specific block issues

### When to Use Combined Plots  
```python
processor.plot_geometry_surface_contours_combined()  # New method
```
- **System-wide** field analysis
- **Comparing** values between blocks
- **Presentation** graphics showing complete geometry
- **Understanding** overall flow patterns

## Integration Benefits

### Automated Variable Processing
The updated script automatically:
1. **Scans all blocks** to find available variables
2. **Groups blocks** by variable availability  
3. **Creates combined plots** for each unique variable
4. **Skips variables** not found in any blocks

### Reduced File Count
- **Before**: 5 blocks × 4 variables = 20 files
- **After**: 4 variables = 4 files
- Much easier to manage and review results

### Consistent Visualization
- All plots use same color schemes and scales
- Easier to compare different variables
- Professional presentation quality

## Technical Implementation

### Color Scale Consistency
```python
# Collect all field values across all blocks
all_field_values = []
for block in blocks:
    block_values = extract_values(block, field_name)
    all_field_values.extend(block_values)

# Set consistent min/max for all blocks
field_min, field_max = min(all_field_values), max(all_field_values)
for trace in figure.data:
    trace.cmin = field_min
    trace.cmax = field_max
```

### Block Identification
- Each block appears as separate mesh trace in Plotly
- Legend automatically generated with block names
- Individual blocks can be toggled on/off
- Consistent styling across all blocks

## Workflow Integration

### Step 1: Enable Block 8
Uncomment the Block 8 section in `post_processing_clean.py`

### Step 2: Run Processing
```bash
python post_processing_clean.py
```

### Step 3: Review Results
Check `surface_contours/` for combined HTML files

### Step 4: Interactive Analysis
- Open HTML files in web browser
- Use interactive controls to explore
- Toggle blocks on/off as needed
- Export images for reports

This new approach gives you the complete picture of each variable across your entire CFD geometry while maintaining the ability to see individual block contributions!