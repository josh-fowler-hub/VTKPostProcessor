# PowerPoint Integration Guide for CFD Plots

## Overview
This guide shows you how to get your CFD visualizations into PowerPoint presentations. We now support both interactive HTML files and PowerPoint-ready PNG exports.

## Quick Setup for PNG Export

### Option 1: Install Kaleido (Recommended)
```bash
pip install kaleido
```
This enables automatic PNG export alongside HTML files.

### Option 2: Alternative Methods
If kaleido installation fails, use these alternatives:
- Manual screenshot capture
- Browser automation tools
- Online conversion services

## What You Get

### Automatic PNG Generation
When you run the post-processing script with kaleido installed:

```
📁 surface_contours/
├── geometry_surface_contour_combined_pressure_all_blocks.html    # Interactive
├── geometry_surface_contour_combined_pressure_all_blocks.png     # PowerPoint ready
├── geometry_surface_contour_combined_velocity_all_blocks.html
├── geometry_surface_contour_combined_velocity_all_blocks.png
└── ...

📁 powerpoint_images/
├── geometry_surface_contour_combined_pressure_all_blocks.png     # Copied for easy access
├── geometry_surface_contour_combined_velocity_all_blocks.png
└── ...
```

### Image Specifications
- **Resolution**: 1200×900 pixels
- **Scale**: 2x for high-DPI displays
- **Format**: PNG with transparency support
- **Quality**: Publication-ready

## PowerPoint Integration Methods

### Method 1: Direct PNG Insert (Recommended)
1. **Run post-processing script** with kaleido installed
2. **Navigate to** `powerpoint_images/` folder
3. **In PowerPoint**: Insert → Pictures → This Device
4. **Select** the PNG files you want
5. **Resize** as needed in PowerPoint

**Pros**: High quality, fast loading, easy editing
**Cons**: Static images (no interactivity)

### Method 2: HTML File Embedding
1. **Run post-processing script** to generate HTML files
2. **In PowerPoint**: Insert → Object → Create from File
3. **Browse** to HTML file in `surface_contours/` folder
4. **Check** "Display as icon" for cleaner appearance

**Pros**: Interactive when clicked, full functionality
**Cons**: Requires internet, larger file sizes

### Method 3: Screenshot Method (Fallback)
If PNG export fails:
1. **Open HTML file** in web browser
2. **Adjust view** (rotate, zoom as desired)
3. **Take screenshot** (Windows: Win+Shift+S)
4. **Paste directly** into PowerPoint

### Method 4: Online Conversion
1. **Upload HTML file** to online converter (htmlcsstoimage.com, etc.)
2. **Download PNG** result
3. **Insert into PowerPoint**

## PowerPoint Best Practices

### Image Quality
```python
# Customize PNG export settings
processor.plot_geometry_surface_contours_combined(
    field_name='pressure',
    save_path='custom_pressure.html'  # Auto-generates custom_pressure.png
)

# The PNG will have:
# - Width: 1200px (suitable for full slide)
# - Height: 900px (16:9 aspect ratio friendly)
# - Scale: 2x (sharp on high-DPI screens)
```

### Slide Layout Tips
- **Full slide**: Use 1200×900 images directly
- **Half slide**: Resize to ~600×450 in PowerPoint
- **Multiple plots**: Use 400×300 for 2×2 grid
- **Comparison**: Side-by-side at 580×435 each

### Professional Presentation
1. **Consistent sizing**: Keep all CFD images same size
2. **Add titles**: Use PowerPoint text boxes for plot titles
3. **Color schemes**: Ensure plot colors match presentation theme
4. **Annotations**: Add arrows/callouts in PowerPoint
5. **Animation**: Use PowerPoint animations for reveal effects

## Advanced PowerPoint Features

### Custom Image Processing
```python
# For specific PowerPoint requirements
def create_powerpoint_optimized_plots():
    # Custom dimensions for specific slide layouts
    processor.plot_geometry_surface_contours_combined(
        field_name='pressure',
        save_path='slides/pressure_full_slide.html'    # 1200×900
    )
    
    # You can modify the method to accept custom dimensions
    # or use image editing software to resize
```

### Batch Processing for Presentations
```python
# Create standardized plots for all variables
variables = ['pressure', 'velocity', 'temperature', 'turbulence']

for var in variables:
    processor.plot_geometry_surface_contours_combined(
        field_name=var,
        save_path=f'presentation/{var}_combined.html'
    )
    # This creates both HTML and PNG versions
```

## Troubleshooting

### PNG Export Issues
**Problem**: "PNG export failed" message
**Solutions**:
1. Install kaleido: `pip install kaleido`
2. Update plotly: `pip install --upgrade plotly`
3. Try alternative: `pip install psutil`
4. Use screenshot method as backup

**Problem**: Poor image quality
**Solutions**:
1. Increase scale factor in code
2. Use larger base dimensions
3. Save as SVG instead (if supported)

### PowerPoint Issues
**Problem**: Images appear blurry
**Solutions**:
1. Use "Insert Picture" instead of copy-paste
2. Don't resize images larger than original
3. Check PowerPoint image compression settings

**Problem**: Large file sizes
**Solutions**:
1. Compress images in PowerPoint
2. Use JPEG instead of PNG for non-transparent images
3. Reduce plot complexity

## Workflow Examples

### Research Presentation
1. **Generate plots**: Run post-processing script
2. **Select key variables**: Choose 2-3 most important fields
3. **Insert PNGs**: Use powerpoint_images/ folder
4. **Add context**: Titles, annotations, conclusions

### Technical Report
1. **Include all variables**: Show comprehensive results
2. **Use consistent layouts**: Same size/position for all plots
3. **Reference HTML files**: Include links for interactive exploration
4. **Document settings**: Note field ranges, scales used

### Client Presentation
1. **Focus on results**: Choose visually impressive plots
2. **Simplify complexity**: Use clear titles and annotations
3. **Professional quality**: High-resolution PNGs
4. **Interactive backup**: Have HTML files ready for questions

## File Organization for PowerPoint

### Recommended Structure
```
📁 presentation_materials/
├── 📁 plots/
│   ├── pressure_plot.png
│   ├── velocity_plot.png
│   └── temperature_plot.png
├── 📁 interactive/
│   ├── pressure_plot.html
│   ├── velocity_plot.html
│   └── temperature_plot.html
└── 📁 powerpoint/
    └── CFD_Results_Presentation.pptx
```

### Template Slide Layouts
Create PowerPoint templates with:
- **Title slide**: Project name, date, author
- **Methods slide**: CFD setup, mesh details
- **Results slides**: One variable per slide
- **Comparison slides**: Multiple variables side-by-side
- **Conclusions slide**: Key findings

This approach gives you maximum flexibility for professional CFD presentations while maintaining the option for interactive exploration when needed!