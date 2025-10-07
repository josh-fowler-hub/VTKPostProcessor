# Post Processing Script Usage Guide

## Overview
The `post_processing_clean.py` script has been restructured into clearly defined blocks that can be easily commented/uncommented based on your needs.

## Script Structure

### Block 1: SLICE AND AVERAGE DATA GENERATION
**Purpose**: Computes slice-averaged data and saves to CSV files  
**When to use**: First time processing or when you need to regenerate averaged data  
**When to comment out**: When you already have the averaged data CSV files

```python
# =============================================================================
# BLOCK 1: SLICE AND AVERAGE DATA GENERATION
# Comment out this entire block if averaged data already exists
# =============================================================================
```

### Block 2: LOAD EXISTING AVERAGED DATA (Alternative)
**Purpose**: Loads pre-existing CSV files instead of computing  
**When to use**: When you want to skip the averaging computation  
**When to uncomment**: After you've already run Block 1 once

```python
# =============================================================================
# BLOCK 2: LOAD EXISTING AVERAGED DATA (Alternative to Block 1)
# Uncomment this block if you want to load pre-existing averaged data
# =============================================================================
```

### Block 3: VISUALIZATION GENERATION
**Purpose**: Creates all the plots and visualizations  
**Always runs**: This block uses the data from either Block 1 or Block 2

#### Sub-blocks within Block 3:
- **3A: CONTOUR PLOTS** - 2D contour visualizations
- **3B: AVERAGED LINE PLOTS** - Line plots from slice-averaged data  
- **3C: 3D SURFACE PLOTS** - Interactive 3D surface plots

### Block 4: OVERLAY PLOTS FROM AVERAGED DATA
**Purpose**: Creates comparison plots across multiple blocks  
**Always runs**: Generates overlay visualizations

## Usage Scenarios

### Scenario 1: First Time Run (Generate Everything)
```python
# Keep Block 1 active, Block 2 commented out
# All other blocks will run automatically
```
**What happens:**
1. Computes slice averages for all blocks
2. Saves averaged data to CSV files
3. Generates all visualizations
4. Creates overlay plots

### Scenario 2: Re-run Visualizations Only
```python
# Comment out Block 1
# Uncomment Block 2
# Blocks 3 and 4 run automatically
```
**What happens:**
1. Loads existing averaged data from CSV files
2. Regenerates all visualizations
3. Creates overlay plots

**Benefits:**
- Much faster execution (skips averaging computation)
- Useful for tweaking visualization parameters
- Good for testing different plot types

### Scenario 3: Partial Processing
You can also comment out specific sub-blocks within Block 3:

```python
# Comment out SUB-BLOCK 3A if you don't need contour plots
# Comment out SUB-BLOCK 3B if you don't need line plots  
# Comment out SUB-BLOCK 3C if you don't need 3D surfaces
```

## File Outputs

### When Block 1 Runs:
- `averaged_data/` folder with `{block_name}_avg.csv` files

### When Block 3 Runs:
- `contour_plots/` folder with matplotlib contour plots
- `line_plots/` folder with averaged line plots
- `3d_plots/` folder with plotly 3D surface plots

### When Block 4 Runs:
- Additional overlay plots in `line_plots/` folder

## Quick Reference Commands

### To skip averaging (after first run):
1. Comment out entire Block 1
2. Uncomment entire Block 2

### To only regenerate specific plot types:
- Comment out unwanted sub-blocks (3A, 3B, or 3C)

### To add new visualization types:
- Add new sub-blocks within Block 3
- Follow the existing pattern with clear comments

## Example Workflow

**Day 1 - Initial Processing:**
```bash
# Run with Block 1 active (generates data + plots)
python post_processing_clean.py
```

**Day 2 - Visualization Updates:**
```bash
# Edit script: Comment Block 1, Uncomment Block 2
# Run to regenerate plots only (much faster)
python post_processing_clean.py
```

**Day 3 - New Analysis:**
```bash
# Add custom analysis in new sub-blocks
# Data loading handled automatically by Block 2
python post_processing_clean.py
```

## Benefits of This Structure

1. **Flexibility**: Easy to skip expensive computations
2. **Modularity**: Clear separation of data generation vs visualization  
3. **Speed**: Re-run visualizations without recomputing averages
4. **Clarity**: Well-commented blocks make intentions clear
5. **Extensibility**: Easy to add new analysis blocks

## Integration with New Methods

The restructured script works seamlessly with the new flexible methods:

```python
# Can be added to Block 3 as a new sub-block
# =================================================================
# SUB-BLOCK 3D: FLEXIBLE LINE PLOTS
# =================================================================
# Use existing all_dataframes from Block 1 or 2
processor.plot_flexible_lines('y_mid', 'p_avg', datasets=all_dataframes)
```