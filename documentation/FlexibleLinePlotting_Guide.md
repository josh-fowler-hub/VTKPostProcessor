# Flexible Line Plotting with Averaged Datasets

## Overview
The VTKPostProcessor now includes powerful methods for loading slice-averaged datasets and creating flexible line plots with custom X and Y variables. This allows for advanced analysis of CFD data relationships.

## New Methods

### 1. `load_averaged_datasets()`
Loads slice-averaged datasets for specified blocks.

```python
# Load datasets for all blocks
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50, block_name=None)

# Load dataset for single block
df = processor.load_averaged_datasets(coordinate='y', num_slices=50, block_name="inlet")

# Load datasets for specific blocks
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50, 
                                          block_name=["inlet", "outlet"])
```

**Parameters:**
- `coordinate`: Slicing direction ('x', 'y', 'z')
- `num_slices`: Number of slices to create
- `data_type`: 'cell' or 'point' data
- `block_name`: None (all), str (single), or list (multiple) blocks
- `block_id`: Block index (if block_name is None)

**Returns:**
- Single block: DataFrame with averaged data
- Multiple blocks: Dict of {block_name: DataFrame}

### 2. `list_averaged_variables()`
Lists available variables in averaged datasets.

```python
# Check variables for all blocks
variables = processor.list_averaged_variables(coordinate='y', num_slices=10)

# Check variables for specific block
variables = processor.list_averaged_variables(coordinate='y', block_name="domain")
```

**Returns:**
- Single block: List of variable names
- Multiple blocks: Dict of {block_name: [variables]}

### 3. `plot_flexible_lines()`
Creates flexible line plots with custom X and Y variables.

```python
# Standard coordinate vs field plot
files = processor.plot_flexible_lines(
    x_var='y_mid',           # Y-coordinate midpoints
    y_var='p_avg',           # Averaged pressure
    datasets=datasets        # Pre-loaded datasets
)

# Field vs field relationship
files = processor.plot_flexible_lines(
    x_var='p_avg',           # Pressure as X-axis
    y_var='T_avg',           # Temperature as Y-axis
    datasets=datasets
)

# Direct loading (no pre-loaded datasets)
files = processor.plot_flexible_lines(
    x_var='y_mid',
    y_var='U_avg',
    coordinate='y',          # Slicing direction
    num_slices=50,           # Number of slices
    block_name=None          # All blocks
)
```

**Parameters:**
- `x_var`: X-axis variable name
- `y_var`: Y-axis variable name
- `datasets`: Pre-loaded datasets (optional)
- `coordinate`: Slicing direction if loading data
- `num_slices`: Number of slices if loading data
- `block_name`: Block specification if loading data
- `x_label`, `y_label`, `title`: Custom labels/title

**Returns:**
- List of saved file paths (individual + overlay plots)

## Variable Naming Convention

### Coordinate Variables
- `x_mid`, `y_mid`, `z_mid`: Midpoint coordinates of each slice

### Averaged Field Variables
- `{field_name}_avg`: Averaged values (e.g., `p_avg`, `T_avg`, `U_avg`)

## Usage Patterns

### Pattern 1: Load Once, Plot Multiple Times
```python
# Load datasets once
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50, block_name=None)

# Create multiple plots from same data
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=datasets)
processor.plot_flexible_lines('y_mid', 'T_avg', datasets=datasets)
processor.plot_flexible_lines('y_mid', 'U_avg', datasets=datasets)
processor.plot_flexible_lines('p_avg', 'T_avg', datasets=datasets)  # Field vs field
```

### Pattern 2: Direct Plotting
```python
# Let method handle data loading
processor.plot_flexible_lines(
    x_var='y_mid',
    y_var='p_avg',
    coordinate='y',
    num_slices=50,
    block_name=["inlet", "domain", "outlet"]
)
```

### Pattern 3: Explore Available Variables
```python
# Check what variables are available
variables = processor.list_averaged_variables()
print("Available variables:", variables)

# Plot interesting relationships
processor.plot_flexible_lines('p_avg', 'T_avg')  # Pressure-temperature
processor.plot_flexible_lines('U_avg', 'p_avg')  # Velocity-pressure
```

## Plot Types Generated

### Individual Plots
- One plot per block showing the X-Y relationship
- Automatic filename: `flexible_line_{y_var}_vs_{x_var}_{block_name}.png`

### Overlay Plots
- When multiple blocks: Combined plot showing all blocks
- Automatic filename: `flexible_overlay_{y_var}_vs_{x_var}.png`

## Advanced Examples

### Example 1: Pressure Distribution Analysis
```python
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=100)

# Traditional profile plot
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=datasets,
                            x_label='Height (m)', y_label='Pressure (Pa)')

# Pressure gradient analysis
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=datasets,
                            title='Pressure Gradient Analysis')
```

### Example 2: Multi-Variable Correlation Study
```python
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50)

# Velocity-pressure correlation
processor.plot_flexible_lines('U_avg', 'p_avg', datasets=datasets,
                            x_label='Velocity (m/s)', y_label='Pressure (Pa)',
                            title='Velocity-Pressure Correlation')

# Temperature-pressure relationship
processor.plot_flexible_lines('T_avg', 'p_avg', datasets=datasets,
                            x_label='Temperature (K)', y_label='Pressure (Pa)',
                            title='Temperature-Pressure Relationship')
```

### Example 3: Cross-Sectional Comparison
```python
# Compare different cross-sections
y_sections = processor.load_averaged_datasets(coordinate='y', num_slices=30)
x_sections = processor.load_averaged_datasets(coordinate='x', num_slices=30)

# Y-direction profiles
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=y_sections,
                            title='Vertical Pressure Profile')

# X-direction profiles  
processor.plot_flexible_lines('x_mid', 'p_avg', datasets=x_sections,
                            title='Horizontal Pressure Profile')
```

## Error Handling
- Missing variables are reported with available alternatives
- Individual block failures don't stop batch processing
- Empty datasets are skipped with warnings
- NaN values are automatically filtered out

## Performance Tips
1. **Load once, plot multiple**: Use `load_averaged_datasets()` once, then plot multiple variables
2. **Check variables first**: Use `list_averaged_variables()` to see what's available
3. **Adjust slice count**: Use fewer slices (`num_slices=20-50`) for quick exploration
4. **Specific blocks**: Plot only needed blocks to save time

## Integration with Existing Methods
The new flexible plotting works alongside existing methods:

```python
# Traditional methods
processor.plot_contour_matplotlib(field_name='p', block_name=None)
processor.plot_averaged_lines(coordinate='y', block_name=None)

# New flexible methods
datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50)
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=datasets)
```