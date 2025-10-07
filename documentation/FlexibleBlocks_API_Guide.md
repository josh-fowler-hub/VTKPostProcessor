# Flexible Block Specification API Documentation

## Overview
All plotting methods in VTKPostProcessor now support flexible block specification through the `block_name` parameter:

- **`block_name=None`**: Process ALL blocks in the dataset
- **`block_name="block_name"`**: Process a SINGLE block by name
- **`block_name=["block1", "block2"]`**: Process MULTIPLE specific blocks

## Updated Methods

### 1. `plot_contour_matplotlib()`
```python
# Plot contours for all blocks
files = processor.plot_contour_matplotlib(field_name='p', block_name=None)

# Plot contour for single block
files = processor.plot_contour_matplotlib(field_name='p', block_name="inlet")

# Plot contours for specific blocks
files = processor.plot_contour_matplotlib(field_name='p', block_name=["inlet", "outlet"])
```

### 2. `plot_contour_plotly_surface()`
```python
# 3D surfaces for all blocks
files = processor.plot_contour_plotly_surface(field_name='p', block_name=None)

# 3D surface for single block
files = processor.plot_contour_plotly_surface(field_name='p', block_name="domain")

# 3D surfaces for multiple blocks
files = processor.plot_contour_plotly_surface(field_name='p', block_name=["domain", "walls"])
```

### 3. `plot_line_vs_coordinate()`
```python
# Line plots for all blocks
files = processor.plot_line_vs_coordinate(field_name='p', coordinate='y', block_name=None)

# Line plot for single block
files = processor.plot_line_vs_coordinate(field_name='p', coordinate='y', block_name="centerline")

# Line plots for multiple blocks
files = processor.plot_line_vs_coordinate(field_name='p', coordinate='y', block_name=["inlet", "outlet"])
```

### 4. `plot_averaged_lines()`
```python
# Slice-averaged lines for all blocks
files = processor.plot_averaged_lines(coordinate='y', block_name=None)

# Slice-averaged lines for single block
files = processor.plot_averaged_lines(coordinate='y', block_name="domain")

# Slice-averaged lines for multiple blocks
files = processor.plot_averaged_lines(coordinate='y', block_name=["domain", "walls"])
```

### 5. `plot_overlay_averaged_lines()`
```python
# Overlay plot with all blocks
file_path = processor.plot_overlay_averaged_lines(field_name='p', coordinate='y', block_name=None)

# Overlay plot with specific blocks
file_path = processor.plot_overlay_averaged_lines(field_name='p', coordinate='y', 
                                                block_name=["inlet", "outlet"])
```

## Return Values

### Multiple Block Processing
When processing multiple blocks, methods return a **list of file paths**:
```python
files = processor.plot_contour_matplotlib(field_name='p', block_name=None)
# Returns: ['contour_p_Block_0_inlet.png', 'contour_p_Block_1_outlet.png', ...]
```

### Single Block Processing
When processing a single block, methods still return a **list** for consistency:
```python
files = processor.plot_contour_matplotlib(field_name='p', block_name="inlet")
# Returns: ['contour_p_inlet.png']
```

### Automatic File Naming
When `save_path=None`, files are automatically named with block identifiers:
- All blocks: `plot_type_field_BlockName.ext`
- Single block: `plot_type_field_BlockName.ext`
- Multiple blocks: `plot_type_field_BlockName.ext` for each

When `save_path` is provided and multiple blocks are processed:
- Base filename is modified: `base_BlockName.ext`

## Error Handling
Individual block failures don't stop the entire operation:
```python
files = processor.plot_contour_matplotlib(field_name='invalid_field', block_name=None)
# Will attempt all blocks, skip failures, return successful files only
```

## Backward Compatibility
The old `block_id` parameter is still supported for single block access by index:
```python
# Still works
files = processor.plot_contour_matplotlib(field_name='p', block_id=0)
```

## Example Usage Patterns

### Process All Blocks for Multiple Variables
```python
variables = ['p', 'U', 'T']
for var in variables:
    files = processor.plot_contour_matplotlib(field_name=var, block_name=None)
    print(f"Generated {len(files)} {var} contour plots")
```

### Compare Specific Blocks
```python
comparison_blocks = ["inlet", "outlet", "center"]
files = processor.plot_averaged_lines(coordinate='y', block_name=comparison_blocks)
```

### Generate Complete Analysis
```python
# All contours for all blocks
contour_files = processor.plot_contour_matplotlib(field_name='p', block_name=None)

# All 3D surfaces for all blocks  
surface_files = processor.plot_contour_plotly_surface(field_name='p', block_name=None)

# Overlay comparison
overlay_file = processor.plot_overlay_averaged_lines(field_name='p', coordinate='y', block_name=None)
```