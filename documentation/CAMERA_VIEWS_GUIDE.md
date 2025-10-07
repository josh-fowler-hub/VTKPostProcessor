# Camera View Options for CFD Plots

## Overview
You can now control the camera orientation when exporting CFD plots to PNG for PowerPoint. This ensures consistent, professional views for presentations.

## Available Camera Views

### Standard Views
```python
# Standard isometric view (RECOMMENDED for PowerPoint)
camera_view='isometric'          # Perfect for showing 3D geometry clearly

# Orthographic views
camera_view='front'              # Front view (Y-axis direction)
camera_view='side'               # Side view (X-axis direction) 
camera_view='top'                # Top-down view (Z-axis direction)
camera_view='back'               # Back view
camera_view='bottom'             # Bottom-up view
```

### Perspective Views
```python
camera_view='perspective'        # Default perspective view
camera_view='close_isometric'    # Closer isometric (more detail)
camera_view='far_isometric'      # Farther isometric (more context)
```

### Custom Camera Position
```python
custom_camera = {
    'eye': dict(x=2.0, y=1.0, z=1.5),    # Camera position
    'center': dict(x=0, y=0, z=0),       # Look-at point  
    'up': dict(x=0, y=0, z=1)            # Up direction
}
camera_view=custom_camera
```

## Usage Examples

### Basic Usage with Camera Control
```python
from VTKPostProcessor import CFDPostProcessor

processor = CFDPostProcessor('your_data.vtm')

# Create plot with isometric view (best for PowerPoint)
result = processor.plot_geometry_surface_contours_combined(
    field_name='pressure',
    block_name=None,  # All blocks
    camera_view='isometric'  # Standard isometric view
)
```

### Multiple Views for Comparison
```python
views = ['isometric', 'front', 'side', 'top']

for view in views:
    result = processor.plot_geometry_surface_contours_combined(
        field_name='pressure',
        camera_view=view,
        save_path=f'pressure_{view}_view.html'
    )
    print(f"Created {view} view: {result['png']}")
```

### Custom View for Specific Geometry
```python
# Example: Angled view for airfoil analysis
airfoil_view = {
    'eye': dict(x=1.5, y=-2.0, z=0.8),   # Position camera
    'center': dict(x=0, y=0, z=0),       # Look at center
    'up': dict(x=0, y=0, z=1)            # Z-axis up
}

result = processor.plot_geometry_surface_contours_combined(
    field_name='pressure',
    camera_view=airfoil_view,
    save_path='pressure_airfoil_view.html'
)
```

## Updated Post-Processing Script

Your main script now uses isometric view by default:

```python
# In scripts/post_processing_clean.py - Block 8
result = processor.plot_geometry_surface_contours_combined(
    field_name=var_name,
    block_name=blocks_with_variable,
    data_type='cell',
    save_path=geometry_contour_path,
    camera_view='isometric'  # Perfect for PowerPoint presentations
)
```

## PowerPoint Integration Benefits

### Consistent Orientation
- All plots have the same viewing angle
- Professional, uniform appearance
- Easy comparison between different variables

### Optimal Views for Presentation
- **Isometric**: Shows all 3 dimensions clearly
- **Front/Side**: Good for flow direction analysis  
- **Top**: Useful for plan views

### High-Quality PNG Export
- 1200×900 resolution with proper camera angle
- Ready for direct insertion into PowerPoint
- No manual rotation needed

## Camera Position Guidelines

### For General CFD Analysis
```python
camera_view='isometric'     # Best all-around view
```

### For Specific Applications
```python
# External flow (cars, aircraft)
camera_view='isometric'     # Shows full geometry

# Internal flow (pipes, ducts)
camera_view='side'          # Shows flow direction

# Heat exchangers
camera_view='front'         # Shows heat transfer surfaces

# Pumps/turbines
camera_view='isometric'     # Shows complex geometry
```

### For Custom Geometries
```python
# Adjust eye position based on your geometry bounds
custom_view = {
    'eye': dict(x=1.25, y=1.25, z=1.25),  # Standard isometric ratios
    'center': dict(x=0, y=0, z=0),        # Geometry center
    'up': dict(x=0, y=0, z=1)             # Usually Z-up
}
```

## Testing Camera Views

Run the camera view test script to see all options:

```bash
python test_camera_views.py
```

This generates sample plots with all available camera views so you can choose the best one for your specific geometry and analysis.

## Tips for PowerPoint Presentations

1. **Use consistent views** across all variables
2. **Isometric is usually best** for showing 3D geometry
3. **Test different views** with your specific geometry
4. **Consider your audience** - engineers vs. management
5. **Add annotations** in PowerPoint to highlight key features

The camera control ensures your CFD visualizations look professional and consistent in presentations!