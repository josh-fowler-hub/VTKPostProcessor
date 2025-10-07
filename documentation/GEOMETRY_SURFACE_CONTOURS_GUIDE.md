# Geometry Surface Contour Visualization Guide

## Overview
The new `plot_geometry_surface_contours()` method creates 3D visualizations that show field values (pressure, velocity, temperature, etc.) directly on the actual geometry surfaces of your CFD mesh. This gives you the true shape of your geometry with contours painted on the surfaces.

## Key Differences

### Coordinate Projections vs Geometry Surface Contours

**Coordinate Projections** (`plot_surface_contours_plotly()`):
- Projects 3D data onto 2D coordinate planes (X-Y, X-Z, Y-Z)
- Shows field distribution on flat surfaces
- Good for understanding overall flow patterns
- Generates: `surface_contour_pressure_xproj_Block1.html`

**Geometry Surface Contours** (`plot_geometry_surface_contours()`):
- Shows field values on the actual 3D mesh surfaces
- Preserves the true geometry shape (airfoils, pipes, complex geometries)
- Shows how fields vary on the physical boundaries
- Generates: `geometry_surface_contour_pressure_Block1.html`

## Usage Examples

### Basic Usage
```python
from VTKPostProcessor import CFDPostProcessor

processor = CFDPostProcessor('your_data.vtm')

# Single block, cell data
processor.plot_geometry_surface_contours(
    field_name='p',           # pressure field
    data_type='cell',         # or 'point'
    block_name='Block1'       # specific block
)
```

### Flexible Block Specification
```python
# All blocks
processor.plot_geometry_surface_contours(
    field_name='p',
    block_name=None          # All blocks
)

# Multiple specific blocks
processor.plot_geometry_surface_contours(
    field_name='p',
    block_name=['Block1', 'Block3', 'Block5']
)

# Single block by name
processor.plot_geometry_surface_contours(
    field_name='p',
    block_name='Block1'
)
```

### Advanced Options
```python
# Custom save path
processor.plot_geometry_surface_contours(
    field_name='velocity_magnitude',
    data_type='cell',
    block_name='Block1',
    save_path='results/velocity_on_geometry.html'
)

# Different field types
processor.plot_geometry_surface_contours(
    field_name='temperature',   # Any available field
    data_type='point',          # Point-based data
    block_name=None            # All blocks
)
```

## Integration with Modular Script

The geometry surface contours are integrated into `post_processing_clean.py` as **BLOCK 8**:

```python
# =============================================================================
# BLOCK 8: GEOMETRY SURFACE CONTOUR PLOTS (PLOTLY 3D MESH)
# Comment out this entire block to skip geometry surface contour generation
# =============================================================================
```

To enable/disable:
- **Enable**: Uncomment the entire Block 8 section
- **Disable**: Comment out the entire Block 8 section

## Output Files

Generated files are saved to `surface_contours/` directory:
- `geometry_surface_contour_<field>_<block>.html` - Interactive 3D plots

## Visualization Features

The generated HTML files provide:
- **Interactive 3D rotation, zoom, pan**
- **Color scale** showing field value ranges
- **Hover information** showing exact values
- **Camera controls** for different viewing angles
- **Export options** for images and data

## When to Use

**Use Geometry Surface Contours when:**
- You want to see the actual shape of your CFD geometry
- Analyzing boundary conditions and wall effects
- Visualizing heat transfer on surfaces
- Understanding pressure distributions on complex geometries
- Presenting results that show real-world geometry

**Use Coordinate Projections when:**
- Analyzing overall flow patterns in a domain
- Looking at cross-sections through the flow
- Comparing different regions of the domain
- Quick overview of field distributions

## Technical Notes

- Uses VTK's `vtkDataSetSurfaceFilter` to extract 3D surfaces
- Converts quad cells to triangular faces for Plotly compatibility
- Handles both cell-centered and point-centered data
- Maps field values to surface mesh with proper interpolation
- Optimized for interactive visualization in web browsers

## Troubleshooting

**Common Issues:**
1. **No surface extracted**: Check if your mesh has 3D cells that can generate surfaces
2. **Field not found**: Verify field name exists in the block
3. **Empty visualization**: Check data_type ('cell' vs 'point') matches your data
4. **Performance**: Large meshes may load slowly in browser - consider subsampling

**Solutions:**
- Use `processor.get_available_variables(block_name='YourBlock')` to check available fields
- Try both 'cell' and 'point' data types
- Start with a single block to test functionality
- Use the test script to verify everything works