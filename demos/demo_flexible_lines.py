#!/usr/bin/env python3
"""
Demonstration of flexible line plotting with averaged datasets
"""

from VTKPostProcessor import VTKPostProcessor

def demo_flexible_line_plots():
    """Demonstrate the new flexible line plotting capabilities"""
    
    # Initialize processor - adjust path to your VTU file
    vtk_file = 'path_to_your.vtu'  # Replace with actual path
    processor = VTKPostProcessor(vtk_file)
    
    print("\n" + "="*70)
    print("Flexible Line Plotting with Averaged Datasets Demo")
    print("="*70)
    
    # Show available blocks
    print(f"\nAvailable blocks: {processor.block_names}")
    
    # 1. List available variables in averaged datasets
    print("\n1. Checking available variables in averaged datasets:")
    try:
        variables = processor.list_averaged_variables(coordinate='y', num_slices=20, block_name=None)
        if isinstance(variables, dict):
            for block, vars_list in variables.items():
                print(f"   {block}: {vars_list}")
        else:
            print(f"   Variables: {variables}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 2. Load averaged datasets for all blocks
    print("\n2. Loading averaged datasets for all blocks:")
    try:
        datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50, block_name=None)
        if isinstance(datasets, dict):
            print(f"   Loaded {len(datasets)} datasets")
            for block_name, df in datasets.items():
                print(f"   {block_name}: {len(df)} data points, {len(df.columns)} variables")
        else:
            print(f"   Single dataset: {len(datasets)} data points, {len(datasets.columns)} variables")
    except Exception as e:
        print(f"   Error: {e}")
        datasets = None
    
    if datasets is not None:
        # 3. Plot standard coordinate vs field (Y-coordinate vs pressure)
        print("\n3. Standard plot: Pressure vs Y-coordinate")
        try:
            files = processor.plot_flexible_lines(
                x_var='y_mid',           # Y-coordinate (midpoint of slice)
                y_var='p_avg',           # Averaged pressure
                datasets=datasets,       # Use pre-loaded data
                x_label='Y Coordinate',
                y_label='Pressure (Pa)',
                title='Pressure Distribution vs Height'
            )
            print(f"   Generated {len(files)} plots")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 4. Plot field vs field (Temperature vs Pressure)
        print("\n4. Field vs Field plot: Temperature vs Pressure")
        try:
            files = processor.plot_flexible_lines(
                x_var='p_avg',           # Averaged pressure
                y_var='T_avg',           # Averaged temperature (if available)
                datasets=datasets,
                x_label='Pressure (Pa)',
                y_label='Temperature (K)',
                title='Temperature vs Pressure Relationship'
            )
            print(f"   Generated {len(files)} plots")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 5. Plot velocity magnitude vs coordinate
        print("\n5. Velocity magnitude vs Y-coordinate")
        try:
            files = processor.plot_flexible_lines(
                x_var='y_mid',
                y_var='U_avg',           # Velocity magnitude (if available)
                datasets=datasets,
                x_label='Y Coordinate',
                y_label='Velocity Magnitude (m/s)',
                title='Velocity Profile vs Height'
            )
            print(f"   Generated {len(files)} plots")
        except Exception as e:
            print(f"   Error: {e}")
    
    # 6. Generate plots without pre-loading (let method handle loading)
    print("\n6. Direct plotting without pre-loading datasets:")
    try:
        files = processor.plot_flexible_lines(
            x_var='y_mid',
            y_var='p_avg',
            datasets=None,           # Let method load data
            coordinate='y',          # Slicing direction
            num_slices=30,           # Number of slices
            block_name=None,         # All blocks
            x_label='Height (m)',
            y_label='Pressure (Pa)',
            title='Direct Loading - Pressure vs Height'
        )
        print(f"   Generated {len(files)} plots")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 7. Plot for specific blocks only
    if len(processor.block_names) >= 2:
        print("\n7. Plotting for specific blocks only:")
        selected_blocks = processor.block_names[:2]
        try:
            files = processor.plot_flexible_lines(
                x_var='y_mid',
                y_var='p_avg',
                coordinate='y',
                num_slices=25,
                block_name=selected_blocks,  # Specific blocks
                x_label='Y Coordinate',
                y_label='Pressure (Pa)',
                title=f'Pressure Profile - {", ".join(selected_blocks)}'
            )
            print(f"   Generated {len(files)} plots for blocks: {selected_blocks}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "="*70)
    print("Flexible Line Plotting Demo Complete!")
    print("="*70)
    
    # Show example usage patterns
    print("\nExample Usage Patterns:")
    print("----------------------")
    print("# List variables first:")
    print("vars = processor.list_averaged_variables()")
    print("")
    print("# Load datasets once, use multiple times:")
    print("datasets = processor.load_averaged_datasets(coordinate='y', num_slices=50)")
    print("processor.plot_flexible_lines('y_mid', 'p_avg', datasets=datasets)")
    print("processor.plot_flexible_lines('y_mid', 'T_avg', datasets=datasets)")
    print("")
    print("# Plot field vs field relationships:")
    print("processor.plot_flexible_lines('p_avg', 'T_avg', datasets=datasets)")
    print("")
    print("# Plot specific blocks:")
    print("processor.plot_flexible_lines('y_mid', 'U_avg', block_name=['inlet', 'outlet'])")

if __name__ == "__main__":
    demo_flexible_line_plots()